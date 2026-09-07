# Add search to the items list

## Context

Users have asked for a way to find an item without scrolling through every
page of the list. The backlog ticket just says "add search to items" -
it doesn't say which fields, or whether search should still respect who
owns what.

## Goals

- Let a caller filter GET /items/ down to items matching a search term in
  the title or description.
- Preserve the endpoint's existing per-user visibility: a non-superuser
  must never see another user's items in search results, exactly as they
  can't today without a search term.
- Preserve the existing pagination parameters (`skip`, `limit`).

## Non-Goals

- No full-text ranking, fuzzy matching, or relevance scoring. Substring
  match only, case-insensitive.
- No search across other fields (owner name, dates).

## Approach

Add an optional `q` query parameter to `GET /items/`. When present, filter
to items whose `title` OR `description` contains `q`, case-insensitive,
applied *before* the existing ownership `WHERE` clause and pagination -
never after, so a non-superuser's result set is still bounded by their own
items first.

## Success Criteria & Evals

SC-1 — `GET /items/?q=<term>` returns items whose title or description
contains `<term>`, case-insensitively, and excludes items where neither
field contains it.
Eval: tests/ablation/test_task1_search.py::test_search_matches_title_case_insensitive,
tests/ablation/test_task1_search.py::test_search_matches_description

SC-2 — A non-superuser's search results never include another user's
items, even when that item's title/description matches the search term.
Eval: tests/ablation/test_task1_search.py::test_search_still_scopes_by_owner

SC-3 (failure behaviour) — An empty or missing `q` returns the existing
unfiltered, paginated list unchanged - `q` is additive, not a required
parameter, and a malformed/very long `q` does not 500.
Eval: not yet written (manual: `GET /items/?q=` and `GET /items/` return
identical results for the same caller).

## Open Questions

- None. The one real ambiguity (which fields, and does scoping still
  apply) is resolved above rather than left open.
