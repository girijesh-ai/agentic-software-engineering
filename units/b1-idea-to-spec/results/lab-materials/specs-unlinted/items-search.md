# Add search to the items list

## Context

Users have asked for a way to find an item without scrolling through every
page of the list. The backlog ticket just says "add search to items."

## Goals

- Let a caller filter GET /items/ down to items matching a search term.
- Keep the existing pagination and per-user visibility behavior.

## Non-Goals

Not doing full-text ranking or fuzzy matching. Just a substring match.

## Approach

Add an optional `q` query parameter to `GET /items/`. When present, filter
to items whose title or description contains it, case-insensitively.

## Success Criteria & Evals

SC-1 — Searching should work well and return the items the user is
looking for.
Eval: manual testing.

SC-2 — Results still respect the existing pagination parameters.
Eval: tests/ablation/test_task1_search.py

## Open Questions

- None.
