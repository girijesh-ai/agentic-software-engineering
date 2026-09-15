"""C4 task 4: adding a member with a nonexistent user_id must 404, not
silently create a dangling membership row.
"""

import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from tests.utils.user import create_random_user, user_authentication_headers
from tests.utils.utils import random_lower_string


def _headers_for(client: TestClient, db: Session) -> tuple[dict[str, str], object]:
    from app import crud
    from app.models import UserUpdate

    user = create_random_user(db)
    password = random_lower_string()
    crud.update_user(session=db, db_user=user, user_in=UserUpdate(password=password))
    headers = user_authentication_headers(client=client, email=user.email, password=password)
    return headers, user


def _make_team(client: TestClient, owner_headers: dict[str, str]) -> str:
    r = client.post(f"{settings.API_V1_STR}/teams/", headers=owner_headers, json={"name": "Eng"})
    assert r.status_code == 200, r.text
    return r.json()["id"]


def test_adding_a_real_user_still_works(client: TestClient, db: Session) -> None:
    owner_headers, owner = _headers_for(client, db)
    team_id = _make_team(client, owner_headers)
    _, real_user = _headers_for(client, db)

    r = client.post(
        f"{settings.API_V1_STR}/teams/{team_id}/members",
        headers=owner_headers,
        json={"user_id": str(real_user.id), "role": "viewer"},
    )
    assert r.status_code == 200


def test_adding_a_nonexistent_user_is_404(client: TestClient, db: Session) -> None:
    owner_headers, owner = _headers_for(client, db)
    team_id = _make_team(client, owner_headers)
    fake_user_id = uuid.uuid4()

    r = client.post(
        f"{settings.API_V1_STR}/teams/{team_id}/members",
        headers=owner_headers,
        json={"user_id": str(fake_user_id), "role": "viewer"},
    )
    assert r.status_code == 404

    r2 = client.get(f"{settings.API_V1_STR}/teams/{team_id}/members", headers=owner_headers)
    user_ids = {m["user_id"] for m in r2.json()}
    assert str(fake_user_id) not in user_ids
