"""C4 task 3: view a single member's role (GET /teams/{team_id}/members/{user_id})."""

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


def test_member_can_view_another_members_role(client: TestClient, db: Session) -> None:
    owner_headers, owner = _headers_for(client, db)
    team_id = _make_team(client, owner_headers)
    viewer_headers, viewer = _headers_for(client, db)
    _add_member(client, owner_headers, team_id, viewer.id, "viewer")

    r = client.get(
        f"{settings.API_V1_STR}/teams/{team_id}/members/{viewer.id}", headers=owner_headers
    )
    assert r.status_code == 200
    assert r.json()["user_id"] == str(viewer.id)
    assert r.json()["role"] == "viewer"


def test_non_member_denied(client: TestClient, db: Session) -> None:
    owner_headers, owner = _headers_for(client, db)
    team_id = _make_team(client, owner_headers)
    outsider_headers, _ = _headers_for(client, db)

    r = client.get(
        f"{settings.API_V1_STR}/teams/{team_id}/members/{owner.id}", headers=outsider_headers
    )
    assert r.status_code == 403


def test_nonexistent_membership_is_404(client: TestClient, db: Session) -> None:
    owner_headers, owner = _headers_for(client, db)
    team_id = _make_team(client, owner_headers)
    _, stranger = _headers_for(client, db)

    r = client.get(
        f"{settings.API_V1_STR}/teams/{team_id}/members/{stranger.id}", headers=owner_headers
    )
    assert r.status_code == 404
