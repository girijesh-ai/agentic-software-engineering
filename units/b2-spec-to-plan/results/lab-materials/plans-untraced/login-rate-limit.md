# Plan: Add rate limiting to the login endpoint

**Step 1 — Track failed attempts per submitted account, not per caller.**
Add a rate limiter keyed by the submitted email/username on `POST /login/access-token`.
On enough failures within a window, respond 429 to further attempts against that
account, regardless of caller IP.

**Step 2 — Confirm untouched accounts are unaffected.**
An account with no prior failed attempts must log in normally on the first try.
