import uuid
from collections.abc import Callable, Generator
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session

from app.core import security
from app.core.config import settings
from app.core.db import engine
from app.models import Item, Role, TeamMembership, TokenPayload, User

_ROLE_RANK = {Role.viewer: 0, Role.editor: 1, Role.owner: 2}

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator[Session]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except InvalidTokenError, ValidationError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = session.get(User, token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user


def _effective_role(session: Session, item: Item, user: User) -> Role | None:
    """The caller's role on this item, or None if they have no access at all.

    Team role takes priority when the item has a team; otherwise ownership is
    the only path in, matching today's single-owner behaviour unchanged.
    """
    if user.is_superuser:
        return Role.owner
    if item.team_id is not None:
        membership = session.get(TeamMembership, (item.team_id, user.id))
        return membership.role if membership else None
    if item.owner_id == user.id:
        return Role.owner
    return None


def get_item_with_permission(min_role: Role) -> Callable[..., Item]:
    """Dependency factory: load an item and require at least `min_role` on it.

    The single enforcement point for item permissions - see
    units/b2-spec-to-plan/results/lab-materials/plan-team-sharing.md
    "Architecture decision" for why this replaces per-handler inline checks.
    """

    def _dependency(id: uuid.UUID, session: SessionDep, current_user: CurrentUser) -> Item:
        item = session.get(Item, id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        role = _effective_role(session, item, current_user)
        if role is None or _ROLE_RANK[role] < _ROLE_RANK[min_role]:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return item

    return _dependency
