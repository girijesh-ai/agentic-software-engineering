"""C4 task 2: a member can leave a team (DELETE /teams/{team_id}/members/me).

A sole owner cannot leave - the team would have no owner left.
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


def test_member_can_leave_team(client: TestClient, db: Session) -> None:
    owner_headers, owner = _headers_for(client, db)
    team_id = _make_team(client, owner_headers)
    member_headers, member = _headers_for(client, db)
    _add_member(client, owner_headers, team_id, member.id, "viewer")

    r = client.delete(f"{settings.API_V1_STR}/teams/{team_id}/members/me", headers=member_headers)
    assert r.status_code == 200

    r2 = client.get(f"{settings.API_V1_STR}/teams/{team_id}/members", headers=owner_headers)
    user_ids = {m["user_id"] for m in r2.json()}
    assert str(member.id) not in user_ids


def test_sole_owner_cannot_leave(client: TestClient, db: Session) -> None:
    owner_headers, owner = _headers_for(client, db)
    team_id = _make_team(client, owner_headers)

    r = client.delete(f"{settings.API_V1_STR}/teams/{team_id}/members/me", headers=owner_headers)
    assert r.status_code == 409


def test_one_of_two_owners_can_leave(client: TestClient, db: Session) -> None:
    owner_headers, owner = _headers_for(client, db)
    team_id = _make_team(client, owner_headers)
    co_owner_headers, co_owner = _headers_for(client, db)
    _add_member(client, owner_headers, team_id, co_owner.id, "owner")

    r = client.delete(f"{settings.API_V1_STR}/teams/{team_id}/members/me", headers=owner_headers)
    assert r.status_code == 200
