# Plan: Team-based item sharing with roles

Traces to [`spec-team-sharing.md`](spec-team-sharing.md). Every step names the SC(s)
it serves and the verification that proves it. A step with no `SC-n` reference is a
bug in this plan, not an acceptable step — that's the orphan-step gate this unit's
`verify.sh` checks mechanically, not just by convention.

## Architecture decision, made before any code exists

**Permission checks move into one dependency, not eight inline copies.** Today's
`items.py` repeats `current_user.is_superuser or item.owner_id == current_user.id`
per handler (B0's map, § Permissions are not centralized). Adding team roles to eight
separate inline checks would either (a) 8x the same branching logic, or (b) get done
correctly in 3 handlers and forgotten in the other 5 — the second is the realistic
failure mode, not a hypothetical one. Decision: add
`get_item_with_permission(min_role: Role)` to `app/api/deps.py`, a
`Depends`-injectable that loads the item, resolves the caller's effective role
(team role if `item.team_id` is set, else owner-or-superuser), and raises 403 if
`min_role` isn't met. Every item route depends on it instead of repeating the check.
This is a layer-boundary decision, not an implementation detail: `deps.py` owns
permission resolution, route handlers own request/response shaping, `crud.py` owns
persistence. Deciding this now, before Step 3, is the point of B2 — deciding it after
5 routes are written means undoing 5 routes.

## Steps

**Step 1 — Data model: `Team`, `TeamMembership`, `Item.team_id`.**
Add `Team(id, name)`, `TeamMembership(team_id, user_id, role: Enum[owner, editor,
viewer])`, nullable `Item.team_id` (FK, `ON DELETE SET NULL` — deleting a team
un-assigns its items rather than deleting them, since Non-Goals rule out data loss
as a side effect of team management). One Alembic migration.
Serves: SC-1 (schema for membership), SC-6 (nullable `team_id` is exactly what keeps
existing items unaffected).
Verify: `alembic upgrade head` succeeds against a fresh DB; `TeamMembership` and
`Item.team_id` are queryable via a throwaway script, no test suite needed for a
schema-only step.

**Step 2 — `get_item_with_permission` dependency in `api/deps.py`.**
Implements the architecture decision above: given an `item_id` path param and a
`min_role`, load the item, compute effective role (`superuser` > team role via
`TeamMembership` if `team_id` set > `owner_id == current_user.id` if `team_id` is
null > none), compare against `min_role`, raise 404 if the item doesn't exist, 403 if
role is insufficient.
Serves: SC-2, SC-3, SC-4, SC-5, SC-6 — this one function is the sole enforcement
point for all of them, which is the architectural payoff of Step 0's decision.
Verify: unit tests directly against the dependency function for each role x
min_role combination (a truth table, not five copy-pasted integration tests) —
`backend/tests/ablation/test_b2_team_membership.py::test_permission_matrix`.

**Step 3 — Team management endpoints.**
`POST /teams/` (create, caller becomes owner), `POST /teams/{id}/members` (add a
member with a role, owner-only), `DELETE /teams/{id}/members/{user_id}`
(remove, owner-only).
Serves: SC-1, SC-4 (owner manages membership), SC-7 (removal path).
Verify: `test_owner_can_add_member`, `test_owner_full_access`,
`test_removed_member_loses_access`.

**Step 4 — Wire `get_item_with_permission` into existing item routes.**
`GET`/`PUT` require `min_role=viewer`/`editor` respectively; `DELETE` requires
`min_role=owner`. Replace the inline ownership check entirely — this is a deletion
of old logic, not an addition alongside it, per the architecture decision.
Serves: SC-2, SC-3, SC-4, SC-5, SC-6.
Verify: `test_viewer_read_only`, `test_editor_read_write_no_delete`,
`test_owner_full_access`, `test_non_member_denied`, `test_unassigned_item_unchanged`.

**Step 5 — `POST /items/` accepts an optional `team_id`.**
If provided, validate the caller has `editor`-or-above membership in that team before
creating the item with it set; otherwise 403 before any row is written.
Serves: SC-8.
Verify: `test_create_with_team_id_requires_membership`.

**Step 6 — Open question, resolved not deferred: last-owner removal.**
`DELETE /teams/{id}/members/{user_id}` on the team's last owner returns 409, not a
silent no-op or an orphaned ownerless team. (Resolves the spec's open question rather
than carrying it into B3 as ambiguity a builder has to guess at.)
Serves: none directly (not one of SC-1..8) — this is the plan explicitly answering a
spec-level open question, which B2's own traceability rule requires flagging as such
rather than smuggling in as an unnumbered extra behind a real SC.
Verify: a ninth test, `test_cannot_remove_last_owner`, added to the same file.

## Traceability check

| SC | Step(s) |
|---|---|
| SC-1 | 1, 3 |
| SC-2 | 2, 4 |
| SC-3 | 2, 4 |
| SC-4 | 2, 3, 4 |
| SC-5 | 2, 4 |
| SC-6 | 1, 2, 4 |
| SC-7 | 3 |
| SC-8 | 5 |

Every SC has at least one step. Step 6 is the plan's one deliberate non-SC step,
named as such above rather than left implicit.
