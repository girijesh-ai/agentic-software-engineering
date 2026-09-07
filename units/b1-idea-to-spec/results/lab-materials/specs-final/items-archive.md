# Let users archive items instead of deleting them

## Context

Deleting an item is permanent and users have accidentally lost items with
no way to get them back. Ticket: "let users archive items instead of
deleting them."

## Goals

- `DELETE /items/{id}` no longer removes the row from the database.
- Archived items are excluded from the default `GET /items/` list.
- Existing ownership permission checks on delete are unchanged.

## Non-Goals

- No un-archive/restore endpoint in this change - explicitly deferred.
- No change to how archived items are counted elsewhere; only the list
  endpoint's default filtering changes.

## Approach

Add an `is_archived: bool = False` column to `Item`. Change the DELETE
handler to set `is_archived = True` and commit, instead of `session.delete`.
Add a `WHERE is_archived = false` clause to the default list query.

## Success Criteria & Evals

SC-1 — `DELETE /items/{id}` sets `is_archived=True` and the row still
exists in the database afterward (queryable by ID).
Eval: tests/ablation/test_task2_archive.py::test_delete_archives_not_removes

SC-2 — Archived items do not appear in `GET /items/`'s default response.
Eval: tests/ablation/test_task2_archive.py::test_archived_items_excluded_from_default_list

SC-3 (failure behaviour) — Archiving an item that is already archived
returns 200, not an error, and does not change the item otherwise.
Eval: tests/ablation/test_task2_archive.py::test_archiving_twice_is_not_an_error

SC-4 (failure behaviour) — A non-owner attempting to archive someone
else's item still gets 403, unchanged from today's delete behaviour.
Eval: tests/ablation/test_task2_archive.py::test_cannot_archive_someone_elses_item

## Open Questions

- Whether to expose archived items via a filter flag on GET /items/ is
  deferred to a follow-up ticket; not needed for this change.
