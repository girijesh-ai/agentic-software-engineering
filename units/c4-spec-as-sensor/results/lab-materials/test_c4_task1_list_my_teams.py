"""C4 task 1: list teams the current user belongs to (GET /teams/)."""

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


def _make_team(client: TestClient, owner_headers: dict[str, str], name: str = "Eng") -> str:
    r = client.post(f"{settings.API_V1_STR}/teams/", headers=owner_headers, json={"name": name})
    assert r.status_code == 200, r.text
    return r.json()["id"]


def _add_member(client: TestClient, owner_headers: dict[str, str], team_id: str, user_id, role: str) -> None:
    r = client.post(
        f"{settings.API_V1_STR}/teams/{team_id}/members",
        headers=owner_headers,
        json={"user_id": str(user_id), "role": role},
    )
    assert r.status_code == 200, r.text


def test_lists_teams_the_user_belongs_to(client: TestClient, db: Session) -> None:
    owner_headers, owner = _headers_for(client, db)
    team_a = _make_team(client, owner_headers, "Team A")
    team_b = _make_team(client, owner_headers, "Team B")

    member_headers, member = _headers_for(client, db)
    _add_member(client, owner_headers, team_a, member.id, "viewer")

    r = client.get(f"{settings.API_V1_STR}/teams/", headers=member_headers)
    assert r.status_code == 200
    team_ids = {t["id"] for t in r.json()}
    assert team_a in team_ids
    assert team_b not in team_ids


def test_user_with_no_teams_sees_empty_list(client: TestClient, db: Session) -> None:
    headers, _ = _headers_for(client, db)
    r = client.get(f"{settings.API_V1_STR}/teams/", headers=headers)
    assert r.status_code == 200
    assert r.json() == []


def test_owner_of_two_teams_sees_both(client: TestClient, db: Session) -> None:
    owner_headers, owner = _headers_for(client, db)
    team_a = _make_team(client, owner_headers, "Team A")
    team_b = _make_team(client, owner_headers, "Team B")

    r = client.get(f"{settings.API_V1_STR}/teams/", headers=owner_headers)
    assert r.status_code == 200
    team_ids = {t["id"] for t in r.json()}
    assert {team_a, team_b} <= team_ids
