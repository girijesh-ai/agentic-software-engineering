# Plan: Let users archive items instead of deleting them

**Step 1 — Add an archived flag and change DELETE to set it.**
Add a boolean (or equivalent) field to `Item` marking it archived, defaulting to not
archived. Change `DELETE /items/{id}` to set this flag and commit, instead of removing
the row. Add the needed migration.
Serves: SC-1.

**Step 2 — Exclude archived items from the default list.**
`GET /items/` should not include archived items in its default response.
Serves: SC-2.

**Step 3 — Make archiving idempotent.**
Archiving an already-archived item returns 200, not an error.
Serves: SC-3.

**Step 4 — Keep the existing ownership check.**
A non-owner attempting to archive someone else's item still gets 403, unchanged from
today's delete behaviour.
Serves: SC-4.
