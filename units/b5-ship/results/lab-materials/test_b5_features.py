"""Verifiers for B5's three shipped features - the good ideas from B4's
review round, landed properly this time (B4's seeded bugs fixed).

F1 - list team roster (B4's PR2, clean, landed as reviewed).
F2 - rename team (B4's PR3, fixed: reuses _require_owner, schema in
     models.py, no duplicated permission logic).
F3 - team details by id (B4's PR5, fixed: requires auth AND membership,
     unlike the original unauthenticated version).
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


# --- F1: list team roster -----------------------------------------------

def test_f1_member_can_list_roster(client: TestClient, db: Session) -> None:
    owner_headers, owner = _headers_for(client, db)
    team_id = _make_team(client, owner_headers)
    viewer_headers, viewer = _headers_for(client, db)
    _add_member(client, owner_headers, team_id, viewer.id, "viewer")

    r = client.get(f"{settings.API_V1_STR}/teams/{team_id}/members", headers=viewer_headers)
    assert r.status_code == 200
    user_ids = {m["user_id"] for m in r.json()}
    assert str(owner.id) in user_ids
    assert str(viewer.id) in user_ids


def test_f1_non_member_denied_roster(client: TestClient, db: Session) -> None:
    owner_headers, owner = _headers_for(client, db)
    team_id = _make_team(client, owner_headers)
    outsider_headers, _ = _headers_for(client, db)

    r = client.get(f"{settings.API_V1_STR}/teams/{team_id}/members", headers=outsider_headers)
    assert r.status_code == 403


# --- F2: rename team ------------------------------------------------------

def test_f2_owner_can_rename_team(client: TestClient, db: Session) -> None:
    owner_headers, owner = _headers_for(client, db)
    team_id = _make_team(client, owner_headers)

    r = client.patch(
        f"{settings.API_V1_STR}/teams/{team_id}", headers=owner_headers, json={"name": "New Name"}
    )
    assert r.status_code == 200
    assert r.json()["name"] == "New Name"

    # The critical check: the rename must actually persist, not just echo
    # back in the response (this is the specific bug this feature was
    # seeded with mid-way through B5's lab).
    r2 = client.get(f"{settings.API_V1_STR}/teams/{team_id}/members", headers=owner_headers)
    assert r2.status_code == 200
    from app.models import Team

    db.expire_all()
    team = db.get(Team, team_id)
    assert team is not None
    assert team.name == "New Name", "rename did not persist to the database"


def test_f2_non_owner_cannot_rename_team(client: TestClient, db: Session) -> None:
    owner_headers, owner = _headers_for(client, db)
    team_id = _make_team(client, owner_headers)
    editor_headers, editor = _headers_for(client, db)
    _add_member(client, owner_headers, team_id, editor.id, "editor")

    r = client.patch(
        f"{settings.API_V1_STR}/teams/{team_id}", headers=editor_headers, json={"name": "Hijacked"}
    )
    assert r.status_code == 403


# --- F3: team details by id ------------------------------------------------

def test_f3_member_can_view_team_details(client: TestClient, db: Session) -> None:
    owner_headers, owner = _headers_for(client, db)
    team_id = _make_team(client, owner_headers)

    r = client.get(f"{settings.API_V1_STR}/teams/{team_id}", headers=owner_headers)
    assert r.status_code == 200
    assert r.json()["id"] == team_id


def test_f3_non_member_denied_team_details(client: TestClient, db: Session) -> None:
    owner_headers, owner = _headers_for(client, db)
    team_id = _make_team(client, owner_headers)
    outsider_headers, _ = _headers_for(client, db)

    r = client.get(f"{settings.API_V1_STR}/teams/{team_id}", headers=outsider_headers)
    assert r.status_code == 403


def test_f3_unauthenticated_denied_team_details(client: TestClient, db: Session) -> None:
    owner_headers, owner = _headers_for(client, db)
    team_id = _make_team(client, owner_headers)

    r = client.get(f"{settings.API_V1_STR}/teams/{team_id}")
    assert r.status_code in (401, 403)
