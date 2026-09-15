# Rate limiting

## Context
Login should not be brute-forceable.

## Goals
Limit repeated failed logins.

## Non-goals
Does not cover rate-limiting on any endpoint other than login.

## Success Criteria

### SC-1
After 5 failed logins for the same account within 15 minutes, the 6th
attempt is rejected with 429, even with correct credentials.

Eval: tests/test_login_rate_limit.py::test_sixth_attempt_locked_out

### SC-2
When the rate limiter's backing store is unavailable, login fails closed
(requests rejected with 503) rather than silently allowing unlimited
attempts.

Eval: tests/test_login_rate_limit.py::test_store_down_fails_closed
