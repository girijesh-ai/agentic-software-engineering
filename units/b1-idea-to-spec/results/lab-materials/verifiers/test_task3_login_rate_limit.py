"""Ticket: "Add rate limiting to the login endpoint so repeated failed
attempts don't let someone brute-force a password."

Correct interpretation: the limit tracks the *account being attacked*
(the submitted username/email), not the caller's IP. This is deliberately
the same mistake as README.md section 2's canonical failure: "Rate
limited by IP. Half your traffic is behind one corporate NAT."

No exact attempt-count threshold is asserted here on purpose - a spec
that names one is a spec that made a decision; this test only checks the
part of the ambiguity the ticket actually turns on: per-account vs.
per-IP/global.
"""

from fastapi.testclient import TestClient
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.models import UserCreate
from tests.utils.utils import random_email, random_lower_string

MAX_ATTEMPTS_TO_TRY = 20


def _fail_login(client: TestClient, email: str) -> int:
    r = client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data={"username": email, "password": "definitely-wrong"},
    )
    return r.status_code


def test_repeated_failures_eventually_rate_limited(client: TestClient) -> None:
    email = random_email()
    statuses = [_fail_login(client, email) for _ in range(MAX_ATTEMPTS_TO_TRY)]
    assert 429 in statuses, (
        f"no 429 in {MAX_ATTEMPTS_TO_TRY} failed attempts against one account - "
        "no rate limiting was added at all"
    )


def test_rate_limit_is_per_account_not_per_caller(client: TestClient) -> None:
    attacked_email = random_email()
    for _ in range(MAX_ATTEMPTS_TO_TRY):
        status = _fail_login(client, attacked_email)
        if status == 429:
            break
    else:
        raise AssertionError("attacked account was never rate limited")

    other_email = random_email()
    response = _fail_login(client, other_email)
    assert response != 429, (
        "a different account, from the same caller, was rate limited too - "
        "this is limiting by IP/caller, not by the account being attacked"
    )


def test_correct_login_unaffected_for_untouched_account(
    client: TestClient, db: Session
) -> None:
    email = random_email()
    password = random_lower_string()
    crud.create_user(session=db, user_create=UserCreate(email=email, password=password))

    response = client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data={"username": email, "password": password},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
