# Let a user see their item count without fetching them all

## Context

A user with many items has to page through GET /items/ just to know how
many they have. Ticket: "let a user see how many items they have without
fetching them all."

## Goals

- Provide a way to get just the count, not the full item bodies.

## Non-Goals

- No change to the existing GET /items/ response shape.

## Approach

Add GET /items/count returning {"count": N} for the caller's own items.

## Success Criteria & Evals

SC-1 — GET /items/count returns the caller's own item count.
Eval: tests/ablation/test_task4_item_count.py

## Open Questions

- None.
