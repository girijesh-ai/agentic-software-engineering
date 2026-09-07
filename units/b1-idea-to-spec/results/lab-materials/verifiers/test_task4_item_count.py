"""Ticket: "Let a user see how many items they have without fetching them
all."

Correct interpretation: a dedicated GET /items/count endpoint that returns
just {"count": N} for the caller's own items (all items, for a superuser),
without a `data` payload of item bodies. The existing list endpoint
already returns a `count` field alongside full item bodies, which is not
what "without fetching them all" asks for - this test requires the
lighter-weight surface, not the field that was already there.
"""

from fastapi.testclient import TestClient
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.models import ItemCreate
from tests.utils.user import create_random_user


def test_count_endpoint_matches_owned_items(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    r = client.get(f"{settings.API_V1_STR}/items/count", headers=normal_user_token_headers)
    assert r.status_code == 200
    before = r.json()["count"]
    assert "data" not in r.json(), "this should be a lightweight count, not a data page"

    created = client.post(
        f"{settings.API_V1_STR}/items/",
        headers=normal_user_token_headers,
        json={"title": "counted item", "description": None},
    )
    assert created.status_code == 200

    after = client.get(
        f"{settings.API_V1_STR}/items/count", headers=normal_user_token_headers
    )
    assert after.json()["count"] == before + 1


def test_count_endpoint_does_not_leak_other_users_items(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    other_owner = create_random_user(db)
    before = client.get(
        f"{settings.API_V1_STR}/items/count", headers=normal_user_token_headers
    ).json()["count"]

    for _ in range(3):
        crud.create_item(
            session=db,
            item_in=ItemCreate(title="not mine", description=None),
            owner_id=other_owner.id,
        )

    after = client.get(
        f"{settings.API_V1_STR}/items/count", headers=normal_user_token_headers
    ).json()["count"]
    assert after == before
