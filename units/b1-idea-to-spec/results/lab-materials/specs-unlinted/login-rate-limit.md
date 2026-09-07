# Add rate limiting to the login endpoint

## Context

Repeated failed login attempts let someone brute-force a password. Ticket:
"add rate limiting to the login endpoint so repeated failed attempts don't
let someone brute-force a password."

## Goals

- Stop an attacker from trying unlimited passwords against the login
  endpoint.

## Non-Goals

- CAPTCHA, 2FA, or account lockout notifications - out of scope.

## Approach

Add rate limiting middleware in front of POST /login/access-token. Track
attempts and reject with 429 once a threshold is exceeded.

## Success Criteria & Evals

SC-1 — Repeated failed logins should eventually be rate limited.
Eval: tests/ablation/test_task3_login_rate_limit.py

## Open Questions

- What should the exact threshold be? Left to implementation.
