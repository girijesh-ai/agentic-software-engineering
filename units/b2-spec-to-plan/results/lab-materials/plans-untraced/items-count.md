# Plan: Let a user see their item count without fetching them all

**Step 1 — Add a dedicated count endpoint.**
Add `GET /items/count` returning `{"count": N}` for the caller's own items (all items
for a superuser), with no item bodies in the response. Register it before the
`/{id}` route so `count` isn't swallowed as a UUID path parameter.

**Step 2 — Confirm the count never leaks across users.**
A non-superuser's count must never include another user's items.
