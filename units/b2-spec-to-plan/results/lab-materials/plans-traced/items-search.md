# Plan: Add search to the items list

**Step 1 — Add the `q` query parameter and filter before scoping.**
Add optional `q: str | None = None` to `GET /items/`. When present, filter to items
where `title` OR `description` contains `q` (case-insensitive), applied before the
existing ownership `WHERE` clause.
Serves: SC-1, SC-2.

**Step 2 — Preserve default behaviour when `q` is absent.**
An empty or missing `q` must return the existing unfiltered, paginated list unchanged.
Serves: SC-3.
