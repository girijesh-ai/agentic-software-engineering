"""Ticket: "Let users archive items instead of deleting them."

Correct interpretation: DELETE /items/{id} archives (row stays in the DB)
instead of removing the row. Archived items are excluded from the default
list. Ownership checks are unchanged. Archiving an already-archived item
is idempotent, not an error.

The row-existence check below is deliberately schema-agnostic (raw SQL
row count, not an ORM field like `is_archived`) - a spec-guided arm was
told the exact field name, but an arm with no spec was not, and a
different field name (e.g. `archived_at`) is a legitimate implementation
choice this test must not penalize.
"""

from fastapi.testclient import TestClient
from sqlmodel import Session, text

from app.core.config import settings
from tests.utils.item import create_random_item


def _row_exists(db: Session, item_id) -> bool:
    db.expire_all()
    count = db.exec(
        text("SELECT COUNT(*) FROM item WHERE id = :id"), params={"id": str(item_id)}
    ).one()
    return count[0] == 1


def test_delete_archives_not_removes(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    item = create_random_item(db)
    item_id = item.id

    response = client.delete(
        f"{settings.API_V1_STR}/items/{item_id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    assert _row_exists(db, item_id), "the row must still exist in the database"


def test_archived_items_excluded_from_default_list(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    item = create_random_item(db)
    client.delete(
        f"{settings.API_V1_STR}/items/{item.id}", headers=superuser_token_headers
    )

    response = client.get(
        f"{settings.API_V1_STR}/items/", headers=superuser_token_headers
    )
    assert response.status_code == 200
    ids = {row["id"] for row in response.json()["data"]}
    assert str(item.id) not in ids


def test_archiving_twice_is_not_an_error(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    item = create_random_item(db)
    first = client.delete(
        f"{settings.API_V1_STR}/items/{item.id}", headers=superuser_token_headers
    )
    second = client.delete(
        f"{settings.API_V1_STR}/items/{item.id}", headers=superuser_token_headers
    )
    assert first.status_code == 200
    assert second.status_code == 200


def test_cannot_archive_someone_elses_item(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    item = create_random_item(db)  # owned by a different random user

    response = client.delete(
        f"{settings.API_V1_STR}/items/{item.id}", headers=normal_user_token_headers
    )
    assert response.status_code == 403
