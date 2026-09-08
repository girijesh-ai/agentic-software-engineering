"""Verifier for spec-team-sharing.md / plan-team-sharing.md.

Defines "done" before any of Team, TeamMembership, or Item.team_id exist -
every test here should fail at collection (ImportError) or at the first
assertion against the unmodified template. That is correct; it is what
B3 is for.
"""

from fastapi.testclient import TestClient
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.models import Role, Team, TeamMembership, UserUpdate  # noqa: F401 - defines the contract
from tests.utils.item import create_random_item
from tests.utils.user import create_random_user, user_authentication_headers
from tests.utils.utils import random_lower_string


def _headers_for(client: TestClient, db: Session) -> tuple[dict[str, str], object]:
    user = create_random_user(db)
    password = random_lower_string()
    crud.update_user(session=db, db_user=user, user_in=UserUpdate(password=password))
    headers = user_authentication_headers(client=client, email=user.email, password=password)
    return headers, user


def _make_team(client: TestClient, owner_headers: dict[str, str]) -> str:
    r = client.post(
        f"{settings.API_V1_STR}/teams/", headers=owner_headers, json={"name": "Eng"}
    )
    assert r.status_code == 200, r.text
    return r.json()["id"]


def _add_member(client: TestClient, owner_headers: dict[str, str], team_id: str, user_id, role: str) -> None:
    r = client.post(
        f"{settings.API_V1_STR}/teams/{team_id}/members",
        headers=owner_headers,
        json={"user_id": str(user_id), "role": role},
    )
    assert r.status_code == 200, r.text


def test_owner_can_add_member(client: TestClient, db: Session) -> None:
    owner_headers, owner = _headers_for(client, db)
    team_id = _make_team(client, owner_headers)
    member_headers, member = _headers_for(client, db)
    _add_member(client, owner_headers, team_id, member.id, "viewer")


def test_viewer_read_only(client: TestClient, db: Session) -> None:
    owner_headers, owner = _headers_for(client, db)
    team_id = _make_team(client, owner_headers)
    viewer_headers, viewer = _headers_for(client, db)
    _add_member(client, owner_headers, team_id, viewer.id, "viewer")

    item = create_random_item(db)
    item.team_id = team_id
    db.add(item)
    db.commit()

    read = client.get(f"{settings.API_V1_STR}/items/{item.id}", headers=viewer_headers)
    assert read.status_code == 200

    write = client.put(
        f"{settings.API_V1_STR}/items/{item.id}",
        headers=viewer_headers,
        json={"title": "changed"},
    )
    assert write.status_code == 403


def test_editor_read_write_no_delete(client: TestClient, db: Session) -> None:
    owner_headers, owner = _headers_for(client, db)
    team_id = _make_team(client, owner_headers)
    editor_headers, editor = _headers_for(client, db)
    _add_member(client, owner_headers, team_id, editor.id, "editor")

    item = create_random_item(db)
    item.team_id = team_id
    db.add(item)
    db.commit()

    write = client.put(
        f"{settings.API_V1_STR}/items/{item.id}",
        headers=editor_headers,
        json={"title": "changed"},
    )
    assert write.status_code == 200

    delete = client.delete(f"{settings.API_V1_STR}/items/{item.id}", headers=editor_headers)
    assert delete.status_code == 403


def test_owner_full_access(client: TestClient, db: Session) -> None:
    owner_headers, owner = _headers_for(client, db)
    team_id = _make_team(client, owner_headers)

    item = create_random_item(db)
    item.team_id = team_id
    db.add(item)
    db.commit()

    assert client.get(f"{settings.API_V1_STR}/items/{item.id}", headers=owner_headers).status_code == 200
    assert client.put(
        f"{settings.API_V1_STR}/items/{item.id}", headers=owner_headers, json={"title": "x"}
    ).status_code == 200
    assert client.delete(f"{settings.API_V1_STR}/items/{item.id}", headers=owner_headers).status_code == 200

    other_headers, other = _headers_for(client, db)
    _add_member(client, owner_headers, team_id, other.id, "editor")


def test_non_member_denied(client: TestClient, db: Session) -> None:
    owner_headers, owner = _headers_for(client, db)
    team_id = _make_team(client, owner_headers)
    item = create_random_item(db)
    item.team_id = team_id
    db.add(item)
    db.commit()

    outsider_headers, outsider = _headers_for(client, db)
    for method, kwargs in (
        ("get", {}),
        ("put", {"json": {"title": "x"}}),
        ("delete", {}),
    ):
        response = getattr(client, method)(
            f"{settings.API_V1_STR}/items/{item.id}", headers=outsider_headers, **kwargs
        )
        assert response.status_code == 403


def test_unassigned_item_unchanged(client: TestClient, superuser_token_headers: dict[str, str], db: Session) -> None:
    item = create_random_item(db)
    assert item.team_id is None
    response = client.get(f"{settings.API_V1_STR}/items/{item.id}", headers=superuser_token_headers)
    assert response.status_code == 200

    non_owner_headers, _ = _headers_for(client, db)
    response = client.get(f"{settings.API_V1_STR}/items/{item.id}", headers=non_owner_headers)
    assert response.status_code == 403


def test_removed_member_loses_access(client: TestClient, db: Session) -> None:
    owner_headers, owner = _headers_for(client, db)
    team_id = _make_team(client, owner_headers)
    member_headers, member = _headers_for(client, db)
    _add_member(client, owner_headers, team_id, member.id, "editor")

    item = create_random_item(db)
    item.team_id = team_id
    db.add(item)
    db.commit()

    assert client.get(f"{settings.API_V1_STR}/items/{item.id}", headers=member_headers).status_code == 200

    remove = client.delete(
        f"{settings.API_V1_STR}/teams/{team_id}/members/{member.id}", headers=owner_headers
    )
    assert remove.status_code == 200

    assert client.get(f"{settings.API_V1_STR}/items/{item.id}", headers=member_headers).status_code == 403


def test_create_with_team_id_requires_membership(client: TestClient, db: Session) -> None:
    owner_headers, owner = _headers_for(client, db)
    team_id = _make_team(client, owner_headers)

    ok = client.post(
        f"{settings.API_V1_STR}/items/",
        headers=owner_headers,
        json={"title": "team item", "description": None, "team_id": team_id},
    )
    assert ok.status_code == 200
    assert ok.json()["team_id"] == team_id

    outsider_headers, _ = _headers_for(client, db)
    denied = client.post(
        f"{settings.API_V1_STR}/items/",
        headers=outsider_headers,
        json={"title": "sneaky item", "description": None, "team_id": team_id},
    )
    assert denied.status_code == 403


def test_cannot_remove_last_owner(client: TestClient, db: Session) -> None:
    owner_headers, owner = _headers_for(client, db)
    team_id = _make_team(client, owner_headers)

    response = client.delete(
        f"{settings.API_V1_STR}/teams/{team_id}/members/{owner.id}", headers=owner_headers
    )
    assert response.status_code == 409
