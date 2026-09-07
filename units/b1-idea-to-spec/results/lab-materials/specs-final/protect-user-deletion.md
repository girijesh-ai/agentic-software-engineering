# Prevent a user from being deleted while they still own items

## Context

Deleting a user today silently cascade-deletes their items too
(`app/api/routes/users.py::delete_user`), which has caused data loss when
a superuser didn't realize a user still had items. Ticket: "prevent a user
from being deleted while they still own items."

"Prevent" means block the deletion outright, not delete the items more
quietly. The current cascade-delete already "handles" the conflict in the
sense that it doesn't crash - that is exactly the behaviour this ticket
asks to change, not to keep and make gentler.

## Goals

- `DELETE /users/{id}` fails when the target user owns one or more items.
- A user who owns zero items still deletes exactly as before.

## Non-Goals

- No bulk-reassignment or orphaning of items to a null owner - `owner_id`
  stays `NOT NULL`.
- No new endpoint to "delete a user and their items together" in this
  change; if that's wanted later, it should be an explicit, separate,
  named action, not the default of this endpoint.

## Approach

Before deleting, count the target user's items. If the count is > 0,
return 409 Conflict and do not touch the user or any item. If the count
is 0, delete the user exactly as today.

## Success Criteria & Evals

SC-1 — `DELETE /users/{id}` returns 409 when the target user owns >= 1
item, and afterward both the user and the item still exist.
Eval: tests/ablation/test_task5_protect_user_deletion.py::test_delete_blocked_when_user_owns_items

SC-2 (failure behaviour) — `DELETE /users/{id}` still returns 200 and
deletes the user when they own zero items, unchanged from today.
Eval: tests/ablation/test_task5_protect_user_deletion.py::test_delete_still_works_for_user_with_no_items

## Open Questions

- None.
