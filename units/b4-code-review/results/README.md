# B4 results

`authors-run.json` is 10 real, independent reviews (2 conditions x 5 PRs, 1 review
each), dispatched as fresh, context-isolated agents each following `review-code`'s
actual process. Not a live-coding ablation like B0-C3 - this unit tests review
quality on fixed, hand-constructed diffs with documented ground truth, not agent
behavior on a stochastic coding task. Verified 2026-09-14. See
`units/b4-code-review/README.md` §6 for the numbers - a near-total tie between
conditions that revises the unit's own opening prediction.

`lab-materials/` is what was actually used:

- `prs/ground-truth.md` - the 5 PRs' documented intended defects and correct
  verdicts, written before any review ran.
- `prs/pr{1..5}.diff` - real `git diff` output against B2/B3's reference
  implementation.
- `prs/pr{N}_after_*.py` - the complete post-change file for each PR, since
  `review-code`'s own process requires reading the whole file, not just the diff.

Full review text for all 10 runs is inline in `authors-run.json`'s `agent_tail`
field per run, matching the convention every other unit's results file uses -
no separate per-review files, for the same reason B0-C3 don't have them either.

## Why this unit's ablation has n=1 per cell, not >=3

`tools/ablation.py validate` requires >=3 repeats per (arm, task). This unit
reviews a *fixed* PR against a *fixed* answer key - closer to a graded exam
question than a sampled coding attempt. Repeating it 3x per condition would
mostly measure how consistent one model is with itself on an unchanging input,
not buy the same kind of statistical power repeats buy against B0-C3's
stochastic coding outcomes, and would triple review-agent cost for that. This
is the same disclosed pattern `units/c3-enforcing-architecture` used first for
an analogous reason (see that unit's own README §5) - `verify.sh` checks this
unit's real invariants instead of calling the generic validator, and says why
in its own header comment. `tools/audit.sh`, the repo-wide gate, only checks
`dry_run` and `module_id`, so this doesn't affect the standard gates.

## The headline limitation, stated once more plainly

The reviewers in this ablation had full filesystem read access, not just the
diff and one changed file. Every case where the spec-withheld condition matched
spec-provided did so by reading sibling code elsewhere in the same codebase and
noticing precedent the new PR contradicted - not by guessing. This measures
"spec vs. thorough whole-codebase review," not "spec vs. reading only the
diff," and it measures it on a codebase (B2/B3's) with unusually strong,
consistent internal precedent to lean on. See README §6's three numbered
limitations before treating this as a general claim about review methodology.
