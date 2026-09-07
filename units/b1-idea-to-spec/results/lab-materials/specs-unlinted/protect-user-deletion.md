# Prevent a user from being deleted while they still own items

## Context

Deleting a user today silently deletes their items too, which has caused
data loss when a superuser didn't realize a user still had items. Ticket:
"prevent a user from being deleted while they still own items."

## Goals

- Deleting a user who owns items should not succeed silently.

## Approach

In DELETE /users/{id}, check whether the user owns any items first. If so,
handle it gracefully instead of deleting everything.

## Success Criteria & Evals

SC-1 — Deleting a user with items is handled gracefully.
Eval: tests/ablation/test_task5_protect_user_deletion.py

## Open Questions

- None.
