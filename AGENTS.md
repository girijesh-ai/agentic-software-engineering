# AGENTS.md

A **map, not a manual**. Stays under 120 lines. If you're writing a fifth paragraph
about something, it belongs in `docs/` and this file gets a pointer instead.

Enforced: `tools/audit.sh` fails the build if this file exceeds 120 lines.

## What this repo is

An open-source course on agentic software engineering. The product is documentation,
labs and measurement tooling — not an application.

It is also its own worked example. Learners are told to read our harness as a reference
implementation of what we're asking them to build. Sloppiness here is a content bug.

## Where the truth lives

| Question | Read |
|---|---|
| What is this course contractually required to do? | `docs/COURSE-SPEC.md` |
| What units exist, in what order? | `docs/CURRICULUM.md` |
| How do the 16 skills map to units? | `docs/SKILLS-MAP.md` |
| Why this course and not the two that exist? | `docs/POSITIONING.md` |
| Do we cover CS146S? | `docs/CS146S-COVERAGE.md` |
| What happens when the plugin changes? | `docs/PLUGIN-CONTRACT.md` |
| Is this actually a software engineering course? | `docs/ARCHITECTURE-AUDIT.md` |
| What should we borrow from other skills repos? | `docs/ECOSYSTEM-MAP.md` |
| What is the running thread? | `docs/CURRICULUM.md` § The running thread |
| What shape must a unit take? | `docs/CURRICULUM.md` § Unit shape |
| How is a claim measured? | `tools/ablation.py` |
| What checks a spec? | `tools/spec_lint.py` |

`docs/COURSE-SPEC.md` outranks everything. If a unit and the spec disagree, the spec is
right and the unit is a bug.

## Rules

**Every claim needs a source or a number.** A sentence asserting that some technique
works cites a primary source or points at a results file. "Best practice" is not a
citation. Unsupported, cut it.

**Never invent a result.** `results/*.json` come from `tools/ablation.py` against real
runs. A hand-written plausible table destroys the only thing this course has. If numbers
aren't available yet, mark the section a placeholder and say so.

**Null and negative results ship.** A unit whose harness did nothing is a finding.
Do not quietly retune an experiment until it agrees with the prose.

**Eight required sections per unit** — see `docs/CURRICULUM.md` § Unit shape —
including *What makes this obsolete*. `tools/audit.sh` checks.

**Skills belong to the plugin, not here.** Course content teaches; workflow lives in
`spec-driven-engineering`. If a unit needs a capability the plugin lacks, add it to
`expected_gaps` in `skills.lock.json` and to the gap analysis in `docs/SKILLS-MAP.md`
rather than shipping a shadow skill here. The boundary rule is
`docs/PLUGIN-CONTRACT.md` § 5.

**Reference capabilities, not skill names.** Every unit README carries
`<!-- capabilities: a, b, c -->`. Prose may name the current skill for readability, but
`skills.lock.json` is the contract and the only place a binding is decided.

**Prose style.** Short sentences. No em-dash asides. No "not X, but Y". No stock
openers. Write the way a senior engineer explains something to a peer at a whiteboard.
Cut adverbs.

**Don't teach what ships in the box, or rebuild what the ecosystem maintains.**
`/batch`, `/loop`, `/review`, `/simplify`, `/debug` and Routines are built in; ponytail,
Vercel and Trail of Bits maintain the rest. Teach the built-in first, show where it
stops, then teach past it. `docs/ECOSYSTEM-MAP.md` §§ 2 and 7.

**No dependencies in `tools/`.** Standard library only.

## Commands

```bash
tools/audit.sh                                            # all sensors; exits 0 on main
python3 tools/spec_lint.py docs/COURSE-SPEC.md            # the spec lints itself
python3 tools/ablation.py run cfg.json --dry-run -o /tmp/x.json
python3 tools/ablation.py validate units/b1-*/results/authors-run.json
python3 tools/check_skills_map.py --plugin-dir ../spec-driven-engineering
```

## Definition of done for a unit

1. README has all eight sections.
2. `verify.sh` exists, runs, and its gate traces to a named Success Criterion.
3. `results/authors-run.json` exists, validates, is not a dry run.
4. *Our numbers* reports what actually happened, nulls included.
5. `tools/audit.sh` exits 0.

Failing any of these means it doesn't merge, however good the prose is.

## Known gaps

Kept current so an agent doesn't rediscover them or paper over them:

- `tools/audit.sh` exits 0. B0 and B1 have real results (40, 60 runs). B1's
  hypothesis was falsified (53% -> 100%); wrong-problem failures still need grading.
- Running thread picked (B0): team-based item sharing, same repo B1 used (which
  predates it by design; its 5 tasks are independent tickets). CLI also resolved.
- `tools/ablation.py` records wall-clock and pass/fail, not token cost - a tool gap.
- Fall 2026 claim downgraded to `overlaps` (11 real gaps; `cs146s.map.json`
  `fall_2026_claim`), not written up as new units. Fall 2025 still holds, unweakened.
  `check_coverage.py` COV008 tracks the 11 as disclosed warnings, see COVERAGE §F26.
- CS146S evidence is secondary for 9 of 10 Fall-2025 weeks (COV006); W2 is verified.
- Architecture-audit findings F1-F6 are remediated (see that file's status table). A
  new unit that doesn't advance the running thread is probably a lab step instead.
- `skills.lock.json` is pinned to plugin 1.0.1 and unverified against anything newer.
- `spec_lint.py` is heuristic; it will produce false positives. Its job is to force the
  question. Do not add checks that can't be explained in one sentence.

Agent picking up work here: these, in this order, are the backlog. Pick exactly
one. Do not attempt two.

## What this repo is not

Not an agent framework. Not a beginner harness course — that's
`walkinglabs/learn-harness-engineering`, and we link rather than compete. Not
vendor-neutral theatre: labs name a specific CLI and stack with a documented porting
contract.
