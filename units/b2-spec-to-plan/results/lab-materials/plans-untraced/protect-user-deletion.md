# Plan: Prevent a user from being deleted while they still own items

**Step 1 — Block deletion when the target owns items.**
In `DELETE /users/{id}`, count the target's items before deleting. If the count is
greater than 0, return 409 Conflict and do not touch the user or any item.

**Step 2 — Preserve today's behaviour for users with no items.**
A user who owns zero items still deletes normally, returning 200, unchanged from today.
