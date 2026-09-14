from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import col, func, select

from app.api.deps import CurrentUser, SessionDep, get_item_with_permission
from app.models import (
    Item,
    ItemCreate,
    ItemPublic,
    ItemsPublic,
    ItemUpdate,
    Message,
    Role,
    TeamMembership,
)

router = APIRouter(prefix="/items", tags=["items"])

ViewableItem = Annotated[Item, Depends(get_item_with_permission(Role.viewer))]
EditableItem = Annotated[Item, Depends(get_item_with_permission(Role.editor))]
OwnedItem = Annotated[Item, Depends(get_item_with_permission(Role.owner))]


@router.get("/", response_model=ItemsPublic)
def read_items(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve items.
    """

    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Item)
        count = session.exec(count_statement).one()
        statement = (
            select(Item).order_by(col(Item.created_at).desc()).offset(skip).limit(limit)
        )
        items = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(Item)
            .where(Item.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Item)
            .where(Item.owner_id == current_user.id)
            .order_by(col(Item.created_at).desc())
            .offset(skip)
            .limit(limit)
        )
        items = session.exec(statement).all()

    items_public = [ItemPublic.model_validate(item) for item in items]
    return ItemsPublic(data=items_public, count=count)


@router.get("/count")
def count_items(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Count the caller's own items (all items, for a superuser), without
    fetching the item bodies. Registered before /{id} so "count" isn't
    swallowed as a UUID path parameter.
    """
    statement = select(func.count()).select_from(Item)
    if not current_user.is_superuser:
        statement = statement.where(Item.owner_id == current_user.id)
    count = session.exec(statement).one()
    return {"count": count}


@router.get("/{id}", response_model=ItemPublic)
def read_item(item: ViewableItem) -> Any:
    """
    Get item by ID.
    """
    return item


@router.post("/", response_model=ItemPublic)
def create_item(
    *, session: SessionDep, current_user: CurrentUser, item_in: ItemCreate
) -> Any:
    """
    Create new item. Optionally assign it to a team the caller has
    editor-or-above membership in.
    """
    if item_in.team_id is not None and not current_user.is_superuser:
        membership = session.get(TeamMembership, (item_in.team_id, current_user.id))
        if not membership or membership.role == Role.viewer:
            raise HTTPException(status_code=403, detail="Not enough permissions")

    item = Item.model_validate(item_in, update={"owner_id": current_user.id})
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.put("/{id}", response_model=ItemPublic)
def update_item(*, session: SessionDep, item: ViewableItem, item_in: ItemUpdate) -> Any:
    """
    Update an item. Now also lets a viewer toggle read status via the same
    endpoint, since read status is metadata rather than content.
    """
    update_dict = item_in.model_dump(exclude_unset=True)
    item.sqlmodel_update(update_dict)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.delete("/{id}")
def delete_item(session: SessionDep, item: OwnedItem) -> Message:
    """
    Delete an item.
    """
    session.delete(item)
    session.commit()
    return Message(message="Item deleted successfully")
