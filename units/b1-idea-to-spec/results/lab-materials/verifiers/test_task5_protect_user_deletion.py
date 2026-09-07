"""Ticket: "Prevent a user from being deleted while they still own items."

Correct interpretation: DELETE /users/{id} returns 409 when the target
owns >=1 item, and neither the user nor the item is touched. A user with
zero items still deletes normally (200).

The trap: today this endpoint already "handles" the conflict by silently
cascade-deleting the user's items first (see app/api/routes/users.py). A
shallow reading of the ticket could leave that behavior in place, or make
it quieter, instead of blocking the deletion - which is the opposite of
what was asked.
"""

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.config import settings
from app.models import Item, User
from tests.utils.item import create_random_item
from tests.utils.user import create_random_user


def test_delete_blocked_when_user_owns_items(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    item = create_random_item(db)
    owner_id = item.owner_id
    item_id = item.id

    response = client.delete(
        f"{settings.API_V1_STR}/users/{owner_id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 409

    db.expire_all()
    assert db.get(User, owner_id) is not None, "the user must not be deleted"
    assert db.exec(select(Item).where(Item.id == item_id)).first() is not None, (
        "the item must not be deleted either"
    )


def test_delete_still_works_for_user_with_no_items(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    user = create_random_user(db)
    user_id = user.id

    response = client.delete(
        f"{settings.API_V1_STR}/users/{user_id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200

    db.expire_all()
    assert db.get(User, user_id) is None
