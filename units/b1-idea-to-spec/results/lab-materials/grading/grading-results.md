# Wrong-problem-failure grading — results

Executed 2026-09-14. Protocol: [`rubric.md`](rubric.md), cases in
[`failed-runs-packet.json`](failed-runs-packet.json) (11 of B1's 60 runs — every
run whose hidden verifier failed). Two independent graders, each given identical
inputs, no shared context, no knowledge of the other's existence.

## What the graders actually were

**Not human.** B1's original protocol (§6) specifies two independent *human*
graders. That didn't happen here — both graders are fresh, context-isolated AI
agents (Claude, general-purpose), dispatched in parallel with the same rubric and
case packet, told nothing about each other. This is a deliberate, disclosed
substitution, not a claim of having satisfied the original protocol. See
"Why this is a live instance of C1's own finding" below for why the substitution
itself is worth taking seriously rather than treating as a formality.

## Result: 11/11 agreement, 0% disagreement rate

| Case | Arm | Task | Grader A | Grader B | Agree? |
|---|---|---|---|---|---|
| 1 | no-harness | items-search | CODE_DEFECT | CODE_DEFECT | yes |
| 2 | no-harness | login-rate-limit | CODE_DEFECT | CODE_DEFECT | yes |
| 3 | no-harness | items-count | NO_ACTION | NO_ACTION | yes |
| 4 | no-harness | items-count | NO_ACTION | NO_ACTION | yes |
| 5 | prompt-only | items-search | NO_ACTION | NO_ACTION | yes |
| 6 | prompt-only | items-search | CODE_DEFECT | CODE_DEFECT | yes |
| 7 | prompt-only | items-archive | CODE_DEFECT | CODE_DEFECT | yes |
| 8 | prompt-only | items-archive | NO_ACTION | NO_ACTION | yes |
| 9 | prompt-only | items-archive | CODE_DEFECT | CODE_DEFECT | yes |
| 10 | prompt-only | items-count | NO_ACTION | NO_ACTION | yes |
| 11 | prompt-only | items-count | NO_ACTION | NO_ACTION | yes |

**Zero WRONG_PROBLEM classifications from either grader, on any of the 11
failures.** Distribution: 5 CODE_DEFECT, 6 NO_ACTION, 0 WRONG_PROBLEM, 0 OTHER —
identical for both graders.

## The honest headline: this doesn't confirm B1's own opening thesis

B1 §2 argues the failure that burns teams is "well-formed code solving the wrong
problem," not malformed code. Graded against B1's own real failures, that's not
what happened here. Every failure was either an execution-level bug in an
otherwise correctly-understood approach (the agent's own summary states the right
approach — case-insensitive search, per-account rate limiting, soft-delete via
`is_archived` — and the implementation broke somewhere: an import error, a
migration that didn't complete) or the agent declining to act at all (asking a
clarifying question in a mode where nobody could answer, or judging that existing
behavior already satisfied the ticket and stopping to ask rather than building).
Neither category is "well-formed code, wrong problem." Report this plainly rather
than reading the two AI graders' 100% agreement as a validation of the sensor-gap
thesis it was meant to test evidence for.

## Why this doesn't settle the question either

Three real limitations, not caveats to bury:

1. **Only failures were graded.** A run can pass the hidden verifier while still
   solving an adjacent or over-scoped version of the problem the test didn't check
   for — B1 §2's own canonical example (a full quota-management subsystem nobody
   asked for) would pass a narrow pytest check if it also happened to satisfy it.
   This protocol structurally cannot see that population. Zero wrong-problem
   failures *among failures* says nothing about wrong-problem solutions *among
   passes*.
2. **Grading was done from self-reported closing summaries, not the actual diff.**
   `tools/ablation.py` never captured diffs (`units/b1-idea-to-spec/results/README.md`
   already flagged this). Both graders' reasoning leans heavily on the agent's own
   description matching or not matching the ticket — which is legible evidence, but
   an agent that misrepresents its own change in its closing summary would fool
   both graders identically, since they're reading the same text.
3. **Perfect agreement is not strong evidence the method generalizes.** These 11
   cases were low-ambiguity by construction: agents either explicitly described the
   correct approach and then hit a legible execution error, or explicitly declined
   to act. Neither leaves much room for two readers to disagree. A genuinely
   contested case — an agent that built something plausible but subtly
   off-requirement — is exactly where two independent graders would be expected to
   diverge, and this sample contains none.

## Why this is a live instance of C1's own finding, not a side note

C1's Gap 1 named this exact problem: this course has one specified inferential
sensor (human grading for wrong-problem failures) and it had never run. Running it
with two AI graders instead of two humans doesn't close that gap — it demonstrates
it. The course's own thesis is that inferential sensors don't reliably catch
"well-formed code solving the wrong problem," and the two graders used here are
inferential sensors. Their unanimous verdict that no wrong-problem failures
occurred is evidence to weigh accordingly: consistent with either "there genuinely
were none in this small, low-ambiguity sample" or "two same-family AI graders share
the same blind spot the humans this protocol specified were meant to avoid." This
report cannot distinguish those from the inside, which is precisely why B1
specified human graders in the first place.
