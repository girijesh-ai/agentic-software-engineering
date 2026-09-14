# B4 · Code → review

**Prerequisites.** B2 (the spec this unit's PRs are reviewed against), B3 (the
reference implementation the PRs are diffs on top of).
**Time.** ~3 hours. **Cost.** Under $5 in agent tokens.

<!-- capabilities: architecture-lens, code-standards, spec-axis-review -->
**Serves.** SC-6, via the ablation in §6.

---

## 1. The question

What is code review actually for, now that finding bugs is automatable?

## 2. The failure

`review-code`'s two-axis design assumes the spec is what catches spec-shaped
bugs and standards checks catch everything else. This unit set out to measure
exactly that split — review the same 5 PRs twice, once with the spec available
(Axis 1 + Axis 2) and once without (Axis 2 only, explicitly reporting "spec
axis skipped"), and see how much the spec actually buys.

It bought nothing measurable. **Every reviewer that had no spec caught every
seeded defect the reviewer with the spec caught — including the two PRs
deliberately built so that only the written spec states the exact rule being
broken** (PR1: a viewer must get 403 on write; PR4: delete is owner-only, not
editor-accessible). Both spec-withheld reviews reconstructed the rule anyway,
not by guessing, but by reading the surrounding codebase and noticing the new
code contradicted an already-correct sibling implementation sitting right next
to it. This is a sharper, more useful failure than "the ablation found nothing"
— it says something specific about *where* the information a good review needs
actually lives, and it isn't only in the spec.

## 3. The idea

### 3.1 Two-axis review, and where B4's own data complicates it

Axis 1 (spec compliance, primary) and Axis 2 (standards and architecture,
secondary) are supposed to catch different failure classes. §6's data says the
split held for *some* of this unit's PRs (PR2's test-coverage gap and PR3/PR5's
standards issues are Axis-2 territory, spec-independent, and both conditions
converged on them, as expected) but did **not** hold cleanly for the two PRs
built to be Axis-1-only catches. A sufficiently thorough Axis 2 pass — the kind
`review-code`'s own Step 3-4 already mandate ("read the entire file," "grep for
all usages," check callers) — found the same violations by a different route:
comparing the new code against already-correct precedent elsewhere in the
file. The two axes aren't as cleanly separable as the framework implies, at
least when the codebase already contains the right answer somewhere else in
it.

### 3.2 The governance rule, exercised for real

`review-code`'s no-spec fallback says: don't skip Axis 1 silently, report
"spec axis skipped — no spec found," then run Axis 2 in full. All five
spec-withheld reviews did exactly this, verbatim, unprompted beyond the
instruction to follow the rule — none of them silently treated the missing
spec as satisfaction, and none of them refused to review just because a spec
was absent. The rule worked as designed; §6's finding is about what happened
*after* that point, once Axis 2 ran in full anyway.

### 3.3 Mental alignment versus mechanical checking

The curriculum's inversion — mental alignment sits below bug-finding, and it's
the part agents can't do — is not directly testable by this unit's ablation
(these are one-shot reviews of PRs against a codebase the reviewer has never
worked in over time, not an ongoing team's shared understanding). What this
unit *can* say: bug-finding itself, here, correlated far more with whether the
reviewer thoroughly cross-referenced sibling code than with whether it had the
spec. That's a narrower claim than "review-code doesn't need specs" — see
§6's limitations before generalizing it.

## 4. The lab

**Step 1 — Construct 5 real PRs with documented ground truth (done for this
unit).** Real diffs (`git diff`) against B2/B3's reference implementation, not
synthetic pseudo-diffs: two spec violations (one direct — SC-2, one subtle —
SC-3's specific role threshold), one standards violation independent of any
spec (DRY, wrong-layer schema), one security issue independent of any spec (no
auth at all), and one clean PR (the null case — a reviewer that invents issues
on clean code is worse than one that finds nothing).
[`ground-truth.md`](results/lab-materials/prs/ground-truth.md) documents the
intended defect and correct verdict for each, written before any review ran.

**Step 2 — Dispatch independent reviews under both conditions.** Ten
independent, context-isolated review agents (5 PRs × 2 conditions), each given
the diff, the complete post-change file (per `review-code`'s own "read the
entire file" step), and — for the spec-provided condition only — B2's actual
spec. Each followed `review-code`'s real process end to end and produced its
structured report (Scope, Spec compliance, Confirmed issues, Plausible issues,
Standards & architecture, Clean, Verdict).

**Step 3 — Score every review against ground truth, not against each other.**
A review "passes" if its verdict matches the documented ground truth
expectation for that PR. This is not a comparison of the two conditions
against each other first — that comparison is downstream of each one being
checked against a fixed, pre-written answer key.

## 5. The gate

```bash
./verify.sh
```

Passes when: `ground-truth.md` and all 5 PR diffs exist and are non-empty;
`results/authors-run.json` is a real (non-dry-run) run with exactly the
`spec-provided` and `spec-withheld` arms, covering all 5 PRs, one review per
(arm, PR) at minimum. Does **not** call `tools/ablation.py validate`
directly — that check requires ≥3 repeats per cell, a shape built for
B0-C3's stochastic coding-agent ablations. Reviewing a fixed, hand-constructed
PR against a fixed answer key is a different kind of measurement (closer to a
graded exam question than a sampled coding attempt); repeating it three times
per condition would mostly test how consistent one model is with itself on
the same static input, not buy the statistical power repeats buy in a
stochastic-outcome ablation. `verify.sh` checks this unit's real invariants
instead, following the same disclosed pattern C3 used first.

## 6. Our numbers

Real run: `results/authors-run.json`, 10 independent reviews (2 conditions ×
5 PRs, 1 review each), Claude general-purpose agents following `review-code`'s
actual process. Verified 2026-09-14.

| Arm | Match rate against ground truth |
|---|---|
| Spec provided | 80% (4/5) |
| Spec withheld | 100% (5/5) |

`spec-withheld` vs `spec-provided`: +20.0pp (95% CI -0.0 to +0.60 —
**inconclusive**, n=5 per arm and the comparison direction is the opposite of
what the unit predicted). The single per-PR table is more informative than
the aggregate:

| PR | Defect type | Spec-provided verdict | Spec-withheld verdict | Ground truth |
|---|---|---|---|---|
| 1 | Spec violation (direct, SC-2) | NEEDS FIXES ✓ | NEEDS FIXES ✓ | NEEDS FIXES |
| 2 | Clean | NEEDS FIXES ✗ | READY ✓ | READY |
| 3 | Standards (DRY), spec-compliant | NEEDS FIXES ✓ | NEEDS FIXES ✓ | NEEDS FIXES |
| 4 | Spec violation (subtle, SC-3) | NEEDS FIXES ✓ | NEEDS FIXES ✓ | NEEDS FIXES |
| 5 | Security (no auth), spec-silent | NEEDS FIXES ✓ | NEEDS FIXES ✓ | NEEDS FIXES |

**The two conditions agreed on the verdict for 4 of 5 PRs, including both
designed specifically to require the spec.** PR1's spec-withheld reviewer
independently read `app/models.py`, confirmed no read-status field exists, and
concluded from that alone that the change was a privilege-escalation
regression — without ever seeing SC-2's text. PR4's spec-withheld reviewer
caught the identical bug by comparing the new endpoint's editor-level check
against `delete_item`'s existing owner-level check in the *same codebase*
and flagging the inconsistency directly — again, without seeing SC-3's text.
Full review text for all 10 runs is in `results/authors-run.json`'s
`agent_tail` field per run.

**The one divergence ran the opposite direction from the ablation's own
prediction.** PR2 (the clean PR) got NEEDS FIXES from the *spec-provided*
reviewer — not because it found a code defect, but because it held the new
endpoint to a stricter test-coverage bar, citing `review-code`'s own "do
existing tests cover the new behavior" step and the visible convention (one
test per permission behavior) in the spec's own eval suite. The
spec-withheld reviewer, without that visible convention to hold the PR
against, called it READY. This is a real, if secondary, finding: having the
spec available didn't change whether a reviewer *found* bugs in this sample,
but it may have changed how strict a bar the reviewer applied — worth
treating as a defensible stricter standard, not a false positive, per
`ground-truth.md`'s own note.

**Why this null result on the primary question doesn't generalize past this
sample, stated plainly:**

1. **The reviewers had full filesystem access, not just the two files named
   in the prompt.** Both spec-withheld reviewers that matched spec-provided
   did so by actively reading sibling files (`app/models.py`, `items.py`)
   the review-code process itself mandates checking ("grep for all usages,"
   "read the entire file"). A reviewer restricted to only the diff and the
   changed file — closer to how a human skimming a PR notification actually
   works — might not have gone looking for that precedent, and the spec
   would then be the only path to the same conclusion. This ablation tests
   "spec vs. thorough codebase-wide review," not "spec vs. reading only the
   diff."
2. **This codebase has unusually strong internal precedent to lean on.**
   B2/B3 built exactly one centralized permission pattern
   (`ViewableItem`/`EditableItem`/`OwnedItem`) and used it consistently. A
   reviewer can reconstruct "what should this PR's role threshold be" by
   analogy to three other call sites that all agree. A codebase with weaker,
   more inconsistent precedent — which is most real codebases, per B0's own
   map of *this* codebase's history before the refactor — would not offer
   the same shortcut, and the spec's information would matter more.
3. **n=1 per (PR, condition), no repeats.** A single review per cell can't
   rule out variance; a different draw from the same model on the same
   inputs might diverge from what's reported here. Unlike B0-C3's stochastic
   coding ablations, this is closer to a graded exam question than a sampled
   attempt, which is the argument in §5 for not padding it with repeats —
   but it's still a real limitation on how far the 100%/80% numbers travel.

## 7. What makes this obsolete

If `review-code` itself starts explicitly instructing reviewers to check new
code against sibling implementations of the same pattern *before* checking the
spec — turning what happened here by incidental thoroughness into a
deliberate, named step — the distinction this unit measured (spec-provided vs
spec-withheld) would stop being the right ablation to run; the better one
would be "precedent-check enabled vs disabled," independent of spec
availability. Separately: on a codebase with genuinely inconsistent internal
precedent (unlike this one, per §6 limitation 2), this entire result could
flip, and that ablation — same design, a messier codebase — is the natural
next one to run before trusting this unit's numbers as a general claim about
review methodology rather than a fact about this specific, unusually
consistent codebase.

## 8. Sources

- `docs/CURRICULUM.md` § B4 — the two-axis framework, the review hierarchy,
  and the governance rule this unit's lab tests directly.
- `claude-engineering-skills/skills/review-code/SKILL.md` — the exact
  seven-step process every dispatched reviewer followed.
- `units/b2-spec-to-plan/results/lab-materials/spec-team-sharing.md` — the
  spec the spec-provided condition was given, and the Success Criteria PR1
  and PR4 were built to violate.
- `units/b3-plan-to-code/results/lab-materials/reference-implementation/` —
  the codebase all 5 PRs are diffs on top of.
- `units/c3-enforcing-architecture/README.md` § 6 — the closely related prior
  finding (a sensor's remediation message has a ceiling it can't write past)
  that this unit's PR4 result echoes from the review side instead of the
  sensor side.
