# Let a user see their item count without fetching them all

## Context

A user with many items has to page through `GET /items/` (which returns
full item bodies) just to know how many they have. Ticket: "let a user see
how many items they have without fetching them all."

Note: `GET /items/` already returns a `count` field today, but only
alongside a full page of item bodies - it doesn't satisfy "without
fetching them all" on its own, since the caller still pays for and
receives item data to get that number.

## Goals

- A caller can get their own item count without the response containing
  item bodies.
- The count is exact and reflects only items the caller owns (or, for a
  superuser, the same count semantics `GET /items/` already uses).

## Non-Goals

- No change to the existing `GET /items/` response shape.
- No caching or approximate counts - exact count only, this data set is
  small enough that it isn't a performance concern yet.

## Approach

Add `GET /items/count` returning `{"count": N}`, registered *before* the
existing `GET /items/{id}` route (id is a UUID path param; registering
`/count` after `/{id}` would make `/count` get swallowed by the id route
and fail with a UUID-parsing error).

## Success Criteria & Evals

SC-1 — `GET /items/count` returns `{"count": N}` where N matches the
caller's own item count, with no `data` key in the response.
Eval: tests/ablation/test_task4_item_count.py::test_count_endpoint_matches_owned_items

SC-2 (failure behaviour / security) — A non-superuser's count never
includes another user's items, even after other users' item counts
change.
Eval: tests/ablation/test_task4_item_count.py::test_count_endpoint_does_not_leak_other_users_items

## Open Questions

- None.
