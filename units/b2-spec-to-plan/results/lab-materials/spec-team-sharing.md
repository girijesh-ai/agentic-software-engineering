# Team-based item sharing with roles

## Context

Items currently belong to exactly one user (`Item.owner_id`, `NOT NULL`, cascade-deletes
with the owner). Every permission check in `backend/app/api/routes/items.py` is
`current_user.is_superuser or item.owner_id == current_user.id` — repeated inline per
handler (see `units/b0-onboarding-a-codebase/results/lab-materials/repo-map.md`). This
is the running thread picked in B0: replace single-owner items with team-owned items
carrying per-member roles, built out across B1 (this spec) through C6.

## Goals

- A user can create a team and invite other existing users to it with a role: owner,
  editor, or viewer.
- An item can belong to a team instead of a single user. Every team member can act on
  a team item according to their role: viewer reads only; editor reads and writes;
  owner reads, writes, deletes, and manages team membership.
- Existing personally-owned items and their permission behavior are unaffected — this
  is additive, not a forced migration of every item into a team.
- A superuser retains full access to everything, as today.

## Non-Goals

- No nested teams, no cross-team item sharing, no per-item overrides of a team
  member's role (role is set at the team level, not the item level).
- No team-level billing, quotas, or invitations-by-email-to-non-users — inviting
  requires the invitee already have an account.
- No UI work in this spec. Track B's B3 builds the backend; frontend is out of scope
  for the running thread's spec/plan/review stages (B1/B2/B4) and picked up, if at
  all, as a stretch in B3.
- No change to how superusers work today.

## Approach

Three approaches considered:

**A — Team owns items directly (chosen).** Add `Team` (id, name) and `TeamMembership`
(team_id, user_id, role). Add nullable `Item.team_id`. When `team_id` is set,
permission is decided by the caller's `TeamMembership.role` for that team, not
`owner_id`; `owner_id` is kept as "created by," informational only, once an item has a
team. When `team_id` is null, today's owner-only behavior is unchanged.
*Why chosen:* additive (Non-Goal: don't force-migrate existing items), and it
introduces exactly one new permission-decision path rather than mutating the existing
one, which keeps the blast radius on `items.py` to "add a branch," not "rewrite every
handler."

**B — Per-item sharing (Google-Docs-style), no team concept.** A many-to-many
`ItemShare(item_id, user_id, role)` table; no `Team` model at all.
*Rejected:* more granular, but doesn't match "team" as the running-thread framing
already committed to in B0, and doesn't scale to "add a new hire, they see the team's
existing items" — the actual scenario motivating this feature — without sharing every
item individually.

**C — Team ownership replaces personal ownership entirely** (`owner_id` becomes
required `team_id`, every user gets an implicit personal team).
*Rejected:* forces a migration of every existing item and every existing test fixture
on day one, for a benefit (conceptual purity) this spec's Non-Goals explicitly don't
need. Approach A gets the same end-state for teams that opt in, for free, later.

## Success Criteria & Evals

SC-1 — A team owner can add an existing user to their team with a role (owner,
editor, or viewer), and that membership is queryable.
Eval: `backend/tests/ablation/test_b2_team_membership.py::test_owner_can_add_member`

SC-2 — A team member with role `viewer` can read a team item via the API but a write
(update or delete) attempt on it returns 403.
Eval: `backend/tests/ablation/test_b2_team_membership.py::test_viewer_read_only`

SC-3 — A team member with role `editor` can read and update a team item, but deleting
it returns 403 (delete is owner-only).
Eval: `backend/tests/ablation/test_b2_team_membership.py::test_editor_read_write_no_delete`

SC-4 — A team member with role `owner` can read, update, delete a team item, and add
or remove other members.
Eval: `backend/tests/ablation/test_b2_team_membership.py::test_owner_full_access`

SC-5 — A user who is not a member of an item's team gets 403 on every operation on
that item, identical to today's non-owner behavior on a personally-owned item.
Eval: `backend/tests/ablation/test_b2_team_membership.py::test_non_member_denied`

SC-6 (failure behaviour) — An item with `team_id = NULL` (not yet assigned to a team)
behaves exactly as today: only its `owner_id` user (or a superuser) can access it.
No regression on the existing single-owner path.
Eval: `backend/tests/ablation/test_b2_team_membership.py::test_unassigned_item_unchanged`

SC-7 (failure behaviour) — Removing a user's team membership immediately revokes
their access to that team's items; a request made after removal returns 403, not a
cached/stale success.
Eval: `backend/tests/ablation/test_b2_team_membership.py::test_removed_member_loses_access`

SC-8 (failure behaviour) — Creating an item with a `team_id` the creator belongs to
(as editor or owner) succeeds and the item is immediately a team item; creating an
item with a `team_id` the creator does *not* belong to fails (403), not a silently
created item nobody but a superuser can reach.
Eval: `backend/tests/ablation/test_b2_team_membership.py::test_create_with_team_id_requires_membership`

## Open Questions

- What happens to a team's items when the team's last owner is removed? Not resolved
  here — flagged for B2's plan to either resolve explicitly as a step or carry
  forward as an explicit open question into B3, not silently decided in code.
- Should `owner_id` on a team item be updatable (reassigning "created by")? Left as
  no for now (informational field only); revisit if a real use case shows up.
