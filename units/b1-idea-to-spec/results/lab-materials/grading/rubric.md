# Wrong-problem-failure grading rubric

For each failed run (verifier exited non-zero), classify into exactly one category
based on the ticket, the agent's own closing summary, and the verifier's failure
excerpt:

- **WRONG_PROBLEM** — the agent built something coherent and plausible, but it does
  not solve the stated ticket: misdiagnosis of the requirement, unrequested extra
  scope, a plausible solution to an adjacent problem, or a specific wrong
  interpretation of an ambiguous requirement (e.g. rate-limiting by IP instead of by
  account, when the ticket didn't specify which). This is the failure class B1's own
  README §2 describes: well-formed code solving the wrong problem.
- **CODE_DEFECT** — the agent correctly understood what the ticket was asking for,
  attempted exactly that, but the implementation has a bug, is incomplete, or has an
  execution-level mistake (wrong API call, syntax/logic error, missed edge case)
  unrelated to misunderstanding the task.
- **NO_ACTION** — the agent made no code change at all: it asked a clarifying
  question and stopped (common in non-interactive `-p` mode, where nobody answers),
  hit an infrastructure error unrelated to the task, or otherwise produced nothing
  to evaluate.
- **OTHER** — does not fit cleanly into the above; explain why in one sentence.

Grade from the evidence given: the ticket text, the agent's own closing summary
(self-reported, not the actual diff — diffs were not preserved from the original
run), and the verifier's failure output. Do not guess beyond what's stated. If the
evidence is genuinely ambiguous between two categories, say so and pick the closer
one rather than inventing a fifth category.

For each of the 11 runs in `failed-runs-packet.json`, output one line:
`<id>: <CATEGORY> — <one-sentence reason>`
