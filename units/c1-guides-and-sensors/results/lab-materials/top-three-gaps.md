# Top three gaps in this repo's own harness

Defended against the coverage map, not asserted from memory.

## Gap 1 — No inferential sensor has ever actually run

The coverage map has exactly one inferential-sensor row: human grading of
"wrong-problem failures," specified in B1 §6 as the column that matters most, because
by construction no computational check catches misdiagnosis. It is still ungraded in
B1, B2, and B3 (`AGENTS.md` § Known gaps has carried this since B1). Meanwhile
`review-code` — an inferential sensor the plugin already ships — has never been wired
into this repo's own CI or any unit's `verify.sh`.

**Why this is the top gap, not just a TODO:** every real number this course has
published (B0 through C1's own meta-analysis) measures pass/fail against a
computational sensor. That is exactly the measurement Böckeler's framework predicts
will miss "well-formed code that solves the wrong problem" — this course's own
opening thesis, from B1 §1. We have been measuring the thing our own thesis says is
*not* the hard part, three units in a row, and naming it each time instead of fixing
it. The fix is not a new tool; it's spending the grading effort B1 already specified.

## Gap 2 — Every inferential guide in this course is author-side, never agent-side

`spec-from-idea`, `plan-from-spec`, and `grill-me` appear in every unit's Sources and
Skills sections. In every ablation this course has run (B0-C1), they were used by the
author to prepare a static artifact — a map, a spec, a plan — that was then handed to
an agent as plain text. No ablated agent has ever been given the *ability* to invoke
one of these skills live, mid-task, to pressure-test its own approach before acting.

**Why this matters:** it means every "guide" this course has measured is
computational by the time it reaches an agent, regardless of how it was produced.
We've tested "does a better static document help" four times (B0, B1, B2, and the
guide-only bucket of this unit's own meta-analysis) and never tested "does letting
the agent pressure-test itself help" at all. That is a real, unexplored variable, not
a hypothetical one — the tooling to test it already exists in the plugin.

## Gap 3 — Sensor timing is 100% end-of-turn, never mid-loop

Every computational sensor in the map fires after the agent declares itself done:
`verify.sh`, every pytest verifier, `audit.sh`, CI. Böckeler's own timing principle
("keep quality left — fast cheap sensors before commit") is stated in C1's own
curriculum text and violated by every ablation this course has run. B3's `test-first`
arm came closest — the agent *could* run the given test itself mid-task — but nothing
required it to, and this course's harness has no way to tell whether it did.

**Why this is a real gap and not a nitpick:** it's the most plausible explanation for
why B3's test-first arm didn't reach 100% (it hit 93%, not a clean sweep) despite
having the strongest intervention this course has measured. An agent that can check
its work early and often should outperform one that can only check it once, at the
end — and this course has never actually separated "a sensor exists" from "a sensor
was used before the final answer," because nothing here measures agent behavior
*during* a run, only its result at the end.
