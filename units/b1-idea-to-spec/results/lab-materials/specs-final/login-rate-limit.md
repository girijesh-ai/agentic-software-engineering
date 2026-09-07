# Add rate limiting to the login endpoint

## Context

Repeated failed login attempts let someone brute-force a password. Ticket:
"add rate limiting to the login endpoint so repeated failed attempts don't
let someone brute-force a password."

The ticket doesn't say *what* the limit tracks. This matters: a large
share of real users sit behind a shared corporate NAT or VPN egress IP,
so limiting by caller IP punishes every innocent coworker the moment one
of them mistypes a password a few times, while doing nothing to stop an
attacker who simply rotates IPs. **The limit must track the account being
attacked (the submitted email), not the caller.**

## Goals

- After repeated failed login attempts against one email address within a
  rolling window, further attempts against *that email* are rejected with
  429, regardless of which IP they come from.
- A different account, attempted from the same caller/IP, is unaffected.

## Non-Goals

- No CAPTCHA, 2FA, or account-lockout email notifications.
- No IP-based limiting layered on top - out of scope for this ticket, and
  would reintroduce the shared-NAT failure mode described above if it were
  the *only* mechanism.
- Exact attempt-count threshold and window length are an implementation
  choice, not fixed by this spec (see Open Questions).

## Approach

Track failed attempts keyed by the submitted `username` (email) from the
login form, not by client IP. On the Nth failure within a rolling window,
respond 429 to further attempts against that email until the window
elapses or a login for that email succeeds (which resets the counter).

## Success Criteria & Evals

SC-1 — Enough repeated failed attempts against one account eventually
receive 429.
Eval: tests/ablation/test_task3_login_rate_limit.py::test_repeated_failures_eventually_rate_limited

SC-2 — While one account is rate limited, a different account attempted
from the same caller is not affected by that limit.
Eval: tests/ablation/test_task3_login_rate_limit.py::test_rate_limit_is_per_account_not_per_caller

SC-3 (failure behaviour) — An account that has never failed a login
attempt logs in normally on the first try; rate limiting must never
false-positive on an untouched account.
Eval: tests/ablation/test_task3_login_rate_limit.py::test_correct_login_unaffected_for_untouched_account

## Open Questions

- Exact threshold/window (e.g. 5 failures / 60s) is left to the
  implementer; this spec fixes the *dimension* (per-account) rather than
  the number, since the number is a tuning knob and the dimension is the
  part that was actually ambiguous in the ticket.
