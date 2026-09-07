# Let users archive items instead of deleting them

## Context

Deleting an item is permanent and users have accidentally lost items with
no way to get them back. Ticket: "let users archive items instead of
deleting them."

## Goals

- Deleting an item no longer removes it from the database.
- Archived items don't clutter the normal item list.

## Approach

Add an `is_archived` boolean to Item, default false. Change the DELETE
endpoint to set it instead of removing the row. Filter archived items out
of the list endpoint by default.

## Success Criteria & Evals

SC-1 — DELETE /items/{id} archives the item instead of removing it.
Eval: tests/ablation/test_task2_archive.py

SC-2 — The item list should be robust to items being archived and not
show them by mistake.
Eval: tests/ablation/test_task2_archive.py

## Open Questions

- Should there be a way to un-archive? Not addressed here.
