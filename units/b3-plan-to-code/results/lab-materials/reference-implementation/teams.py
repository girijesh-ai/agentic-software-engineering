import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Message,
    Role,
    Team,
    TeamCreate,
    TeamMembership,
    TeamMembershipCreate,
    TeamMembershipPublic,
    TeamPublic,
)

router = APIRouter(prefix="/teams", tags=["teams"])


@router.post("/", response_model=TeamPublic)
def create_team(*, session: SessionDep, current_user: CurrentUser, team_in: TeamCreate) -> Any:
    """
    Create a team. The caller becomes its first owner.
    """
    team = Team.model_validate(team_in)
    session.add(team)
    session.commit()
    session.refresh(team)

    membership = TeamMembership(team_id=team.id, user_id=current_user.id, role=Role.owner)
    session.add(membership)
    session.commit()
    return team


def _require_owner(session: SessionDep, team_id: uuid.UUID, current_user: CurrentUser) -> None:
    if current_user.is_superuser:
        return
    membership = session.get(TeamMembership, (team_id, current_user.id))
    if not membership or membership.role != Role.owner:
        raise HTTPException(status_code=403, detail="Not enough permissions")


@router.post("/{team_id}/members", response_model=TeamMembershipPublic)
def add_member(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    team_id: uuid.UUID,
    membership_in: TeamMembershipCreate,
) -> Any:
    """
    Add a member to a team with a role. Owner-only.
    """
    if not session.get(Team, team_id):
        raise HTTPException(status_code=404, detail="Team not found")
    _require_owner(session, team_id, current_user)

    membership = session.get(TeamMembership, (team_id, membership_in.user_id))
    if membership:
        membership.role = membership_in.role
    else:
        membership = TeamMembership(
            team_id=team_id, user_id=membership_in.user_id, role=membership_in.role
        )
    session.add(membership)
    session.commit()
    session.refresh(membership)
    return membership


@router.delete("/{team_id}/members/{user_id}", response_model=Message)
def remove_member(
    *, session: SessionDep, current_user: CurrentUser, team_id: uuid.UUID, user_id: uuid.UUID
) -> Any:
    """
    Remove a member from a team. Owner-only. Cannot remove the last owner.
    """
    if not session.get(Team, team_id):
        raise HTTPException(status_code=404, detail="Team not found")
    _require_owner(session, team_id, current_user)

    membership = session.get(TeamMembership, (team_id, user_id))
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")

    if membership.role == Role.owner:
        owner_count_stmt = (
            select(func.count())
            .select_from(TeamMembership)
            .where(TeamMembership.team_id == team_id, TeamMembership.role == Role.owner)
        )
        owner_count = session.exec(owner_count_stmt).one()
        if owner_count <= 1:
            raise HTTPException(status_code=409, detail="Cannot remove the last owner")

    session.delete(membership)
    session.commit()
    return Message(message="Member removed successfully")
