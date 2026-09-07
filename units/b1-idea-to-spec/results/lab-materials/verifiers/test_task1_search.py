"""Ticket: "Add search to the items list."

Correct interpretation (author's, not the agent's): a `q` query param on
GET /items/ matches title OR description, case-insensitive, while still
respecting the existing per-user ownership scoping and pagination.
"""

from fastapi.testclient import TestClient
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.models import ItemCreate
from tests.utils.user import create_random_user


def _make_item(db: Session, owner_id, title: str, description: str = "x"):
    return crud.create_item(
        session=db,
        item_in=ItemCreate(title=title, description=description),
        owner_id=owner_id,
    )


def test_search_matches_title_case_insensitive(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    owner = create_random_user(db)
    _make_item(db, owner.id, title="Rolling Deploy Guide")
    _make_item(db, owner.id, title="Unrelated Widget")

    response = client.get(
        f"{settings.API_V1_STR}/items/?q=rolling",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    titles = {item["title"] for item in data}
    assert "Rolling Deploy Guide" in titles
    assert "Unrelated Widget" not in titles


def test_search_matches_description(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    owner = create_random_user(db)
    _make_item(db, owner.id, title="Ticket A", description="mentions rollout plan")
    _make_item(db, owner.id, title="Ticket B", description="mentions nothing relevant")

    response = client.get(
        f"{settings.API_V1_STR}/items/?q=rollout",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    titles = {item["title"] for item in response.json()["data"]}
    assert "Ticket A" in titles
    assert "Ticket B" not in titles


def test_search_still_scopes_by_owner(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    other_owner = create_random_user(db)
    _make_item(db, other_owner.id, title="Someone Else's Rolling Item")

    response = client.get(
        f"{settings.API_V1_STR}/items/?q=rolling",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200
    assert response.json()["data"] == []
