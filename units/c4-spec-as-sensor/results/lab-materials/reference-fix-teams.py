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
    TeamRename,
    User,
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


@router.get("/", response_model=list[TeamPublic])
def list_my_teams(*, session: SessionDep, current_user: CurrentUser) -> Any:
    """
    List teams the current user is a member of (any role).
    """
    statement = (
        select(Team)
        .join(TeamMembership, TeamMembership.team_id == Team.id)
        .where(TeamMembership.user_id == current_user.id)
    )
    return session.exec(statement).all()


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

    if not session.get(User, membership_in.user_id):
        raise HTTPException(status_code=404, detail="User not found")

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


def _require_member(session: SessionDep, team_id: uuid.UUID, current_user: CurrentUser) -> None:
    if current_user.is_superuser:
        return
    membership = session.get(TeamMembership, (team_id, current_user.id))
    if not membership:
        raise HTTPException(status_code=403, detail="Not enough permissions")


@router.get("/{team_id}/members", response_model=list[TeamMembershipPublic])
def list_members(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    team_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    List a team's members. Any current member (any role) can see the roster.
    """
    if not session.get(Team, team_id):
        raise HTTPException(status_code=404, detail="Team not found")
    _require_member(session, team_id, current_user)
    statement = (
        select(TeamMembership)
        .where(TeamMembership.team_id == team_id)
        .offset(skip)
        .limit(limit)
    )
    return session.exec(statement).all()


@router.delete("/{team_id}/members/me", response_model=Message)
def leave_team(*, session: SessionDep, current_user: CurrentUser, team_id: uuid.UUID) -> Any:
    """
    Leave a team. Cannot leave if you are the sole owner.
    """
    membership = session.get(TeamMembership, (team_id, current_user.id))
    if not membership:
        raise HTTPException(status_code=404, detail="Not a member of this team")

    if membership.role == Role.owner:
        owner_count_stmt = (
            select(func.count())
            .select_from(TeamMembership)
            .where(TeamMembership.team_id == team_id, TeamMembership.role == Role.owner)
        )
        owner_count = session.exec(owner_count_stmt).one()
        if owner_count <= 1:
            raise HTTPException(status_code=409, detail="Cannot leave as the sole owner")

    session.delete(membership)
    session.commit()
    return Message(message="Left team successfully")


@router.get("/{team_id}/members/{user_id}", response_model=TeamMembershipPublic)
def get_member(
    *, session: SessionDep, current_user: CurrentUser, team_id: uuid.UUID, user_id: uuid.UUID
) -> Any:
    """
    Get a single member's role. Requires the caller to be a current member.
    """
    _require_member(session, team_id, current_user)
    membership = session.get(TeamMembership, (team_id, user_id))
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")
    return membership


@router.get("/{team_id}", response_model=TeamPublic)
def get_team_details(
    *, session: SessionDep, current_user: CurrentUser, team_id: uuid.UUID
) -> Any:
    """
    Get team details. Requires authentication and membership.
    """
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    _require_member(session, team_id, current_user)
    return team


@router.patch("/{team_id}", response_model=TeamPublic)
def rename_team(
    *, session: SessionDep, current_user: CurrentUser, team_id: uuid.UUID, rename_in: TeamRename
) -> Any:
    """
    Rename a team. Owner-only.
    """
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    _require_owner(session, team_id, current_user)
    team.name = rename_in.name
    session.add(team)
    session.commit()
    session.refresh(team)
    return team


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
