# Build order

Where the work happens, in what sequence, and why that sequence.

Written as a handoff. If you're an agent picking this up cold, this file plus
`AGENTS.md` is your brief.

---

## Where

**Claude Code, on a local clone.** Not because it's nicer, but because three of the next
four tasks cannot run anywhere else:

1. **`ablation.py` shells out to an agent CLI.** It runs `claude -p "$(cat …)"` against a
   real repo and scores the diff. No agent CLI, no numbers — and every *Our numbers*
   section in the repo is currently a placeholder that CI is configured to reject.
2. **The plugin only installs in an agent CLI.** `spec-driven-engineering` is the course's
   spine and B1's first lab step. Writing units about skills you can't invoke is how you
   end up describing a workflow instead of testing one.
3. **The repo claims to be its own worked example** (SC-7, and the README says so out
   loud). Building a harness-engineering course by hand, outside a harness, would make
   that claim false in a way readers would eventually notice.

Push to GitHub early — public and empty is fine. The gates want to run in CI, and
`check_coverage.py`, `check_skills_map.py` and `spec_lint.py` are more useful failing on
a PR than passing on your laptop.

**What stays in a chat session:** ecosystem re-surveys (the landscape moves and search is
better there), adversarial review of a finished unit by a reader with no memory of
writing it, and unblocking a specific artifact. Not the build.

---

## Session 0 — make the gates real

Nothing is verifiable until the sensors run. Roughly one session.

```bash
git init && git add -A && git commit -m "course spec, curriculum, tooling"
claude plugin marketplace add girijesh-ai/spec-driven-engineering
claude plugin install spec-driven-engineering@spec-driven-engineering-dev
```

Then, in order:

1. **Write `tools/audit.sh`.** Referenced in six places and doesn't exist. It should check:
   `AGENTS.md` ≤ 120 lines, every `units/*/README.md` has all eight required sections
   including *What makes this obsolete*, internal links resolve, every unit declares
   `<!-- capabilities: … -->`, `CS146S-COVERAGE.md` is under 12 months old, and every
   shipped unit has a non-dry-run `results/authors-run.json`.
   It will fail immediately. That's correct — it's measuring a half-built repo.
2. **Wire CI.** One workflow running `audit.sh`, `spec_lint.py docs/COURSE-SPEC.md`,
   `check_skills_map.py --plugin-dir …`, `check_coverage.py --allow-planned`.
   Expect red on W2 and on missing results. Red-with-known-reasons beats no signal.
3. **Clear the W2 blocker.** Read the actual CS146S Week 2 syllabus, update
   `cs146s.map.json`. Cheapest task in the backlog and it's the only thing standing
   between you and an unasterisked superset claim.

**Done when:** `audit.sh` runs and its failures are all traceable to unwritten content.

## Session 1 — one unit that is actually true

This is the credibility unlock and it should come before any new prose.

B1 is written to depth and every number in it is a placeholder. Until one unit has real
numbers, the measurement discipline is a claim the repo makes about itself.

1. **Write `units/b1-idea-to-spec/verify.sh`** to the gate described in that unit's § 5.
2. **Run the real ablation.** Four arms, per B1's § 6 table: bare prompt, prompt plus
   `CLAUDE.md`, unlinted spec, linted-and-grilled spec. Target repo
   `tiangolo/full-stack-fastapi-template`. Five tasks, three repeats. Budget a few hours
   and a few dollars.
3. **Write up what happened**, including if the answer is "the spec made no measurable
   difference." That result is publishable and the repo says so in three places. If you
   quietly re-run until the number improves, you have broken the only thing this course
   has.

**Done when:** `results/authors-run.json` validates, is not a dry run, and § 6 reports it.

> The *wrong-problem failures* column needs a human grader — by construction no automated
> check catches it, which is the unit's thesis. Two independent graders, publish the
> disagreement rate, protocol in `results/README.md`.

## Sessions 2+ — units, in thread order

**Write them in running-thread order, not by interest.** B0 → B1 → B2 → B3 → B4 → B5 →
C1 → C2 → C3 → C4 → C5 → C6. Each unit's lab consumes the artifact the previous one
produced, so writing C3 before B3 means inventing the violation that C3's linter catches
instead of hitting a real one.

Then A1–A5 and D1–D4, which are order-independent, then the annexes.

Use the spine on itself:

| Step | Skill | Output |
|---|---|---|
| Decide what the unit must do | `spec-from-idea` | Success Criteria for the unit |
| Pressure-test it | `grill-me` | the section you'd have skipped |
| Sequence the writing | `plan-from-spec` | steps traced to those criteria |
| Draft | `implement` | README + `verify.sh` |
| Check | `review-code` | spec axis first, then standards |
| Land | `finish-branch` | gates green, PR |

Every session ends with `tools/audit.sh` and a commit. A session that ends red without a
note in `AGENTS.md` § Known gaps has lost information.

---

## Rules that will save you a rewrite

**One unit per session, one PR per unit.** The context window is the constraint, and B1
took most of one to write properly.

**`handoff` when you're at ~60% context, not 95%.** Quality degrades before it stops.
Your own plugin has the skill; this is the obvious place to use it.

**Don't write a unit you can't ablate.** If you can't describe the two arms, the unit is
an essay. Essays are allowed in `docs/`, not in `units/`.

**Cut before you pad.** C7 was cut when `/batch` shipped. That was the right call and the
next one will feel worse. `AGENTS.md` says don't teach what ships in the box; re-read it
whenever a unit feels like it's straining.

**Publish before it's finished.** Six units with real numbers beat twenty-two with
placeholders, and the README already says v0 out loud. The status block is not an
apology, it's a claim you can keep.

## Order of value, if you only get six sessions

`tools/audit.sh` → B1's real numbers → B0 → B2 → C1 → C3.

That's the brownfield entry, the spine's first two steps, and the two harness units that
change how someone works on Monday. It is a coherent, shippable course on its own, and
everything after it is expansion rather than repair.
