"""C4 task 5: GET /teams/{team_id}/members accepts skip/limit, matching the
same convention items.py already uses (offset/limit, default limit=100).
"""

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


def _add_member(client: TestClient, owner_headers: dict[str, str], team_id: str, user_id, role: str) -> None:
    r = client.post(
        f"{settings.API_V1_STR}/teams/{team_id}/members",
        headers=owner_headers,
        json={"user_id": str(user_id), "role": role},
    )
    assert r.status_code == 200, r.text


def test_default_returns_all_members(client: TestClient, db: Session) -> None:
    owner_headers, owner = _headers_for(client, db)
    team_id = _make_team(client, owner_headers)
    for _ in range(2):
        _, u = _headers_for(client, db)
        _add_member(client, owner_headers, team_id, u.id, "viewer")

    r = client.get(f"{settings.API_V1_STR}/teams/{team_id}/members", headers=owner_headers)
    assert r.status_code == 200
    assert len(r.json()) == 3


def test_limit_caps_the_page(client: TestClient, db: Session) -> None:
    owner_headers, owner = _headers_for(client, db)
    team_id = _make_team(client, owner_headers)
    for _ in range(2):
        _, u = _headers_for(client, db)
        _add_member(client, owner_headers, team_id, u.id, "viewer")

    r = client.get(
        f"{settings.API_V1_STR}/teams/{team_id}/members?skip=0&limit=2", headers=owner_headers
    )
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_skip_moves_past_the_first_page(client: TestClient, db: Session) -> None:
    owner_headers, owner = _headers_for(client, db)
    team_id = _make_team(client, owner_headers)
    for _ in range(2):
        _, u = _headers_for(client, db)
        _add_member(client, owner_headers, team_id, u.id, "viewer")

    r = client.get(
        f"{settings.API_V1_STR}/teams/{team_id}/members?skip=2&limit=2", headers=owner_headers
    )
    assert r.status_code == 200
    assert len(r.json()) == 1
