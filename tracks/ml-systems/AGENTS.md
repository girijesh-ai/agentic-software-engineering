# AGENTS.md

This file is a **map, not a manual**. It stays under 120 lines. If you find yourself
adding a fifth paragraph about something, that content belongs in `docs/` and this
file gets a pointer instead.

Enforced by `tools/audit.sh`, which fails the build if this file exceeds 120 lines.

## What this repo is

An open-source course on harness engineering for ML systems. The product is
documentation, labs and measurement tooling — not an application.

The repo is also its own worked example. Learners are told to read our harness as a
reference implementation. Sloppiness here is a content bug, not just a process bug.

## Where the truth lives

| Question | Read |
|---|---|
| What is this course contractually required to do? | `docs/COURSE-SPEC.md` |
| What modules exist and in what order? | `docs/CURRICULUM.md` |
| Why does this course exist and not the other one? | `docs/POSITIONING.md` |
| What shape must a module take? | `docs/CURRICULUM.md` § Module shape |
| How is a claim measured? | `tools/ablation.py` |

`docs/COURSE-SPEC.md` outranks everything. If a module and the spec disagree, the
spec is right and the module is a bug.

## Rules

**Every claim needs a source or a number.** A sentence asserting that some harness
technique works must cite a primary source or point at a results file. "Best practice"
is not a citation. If you cannot support it, cut it.

**Never invent a result.** `results/*.json` files are produced by `tools/ablation.py`
against real runs. Writing a plausible-looking table by hand destroys the only thing
this course has. If numbers are not available yet, mark the section as a placeholder
and say so out loud.

**Null and negative results ship.** A module whose harness did nothing is a finding.
Report it. Do not quietly retune the experiment until it agrees with the prose.

**Every module README has all eight required sections** (see `docs/CURRICULUM.md`
§ Module shape), including *What makes this obsolete*. `tools/audit.sh` checks this.

**Prose style.** Short sentences. No em-dash asides. No "not X, but Y". No stock
openers like "In today's rapidly evolving landscape". Write the way a senior engineer
explains something to a peer at a whiteboard. Cut adverbs.

**Do not add dependencies to `tools/`.** Standard library only. A measurement tool
that needs its own environment setup is a measurement tool nobody runs.

## Commands

```bash
tools/audit.sh                              # all sensors; must exit 0 on main
python3 tools/ablation.py run cfg.json --dry-run -o /tmp/x.json   # exercise without tokens
python3 tools/ablation.py validate results/authors-run.json       # SC-1/SC-2 conformance
python3 tools/ablation.py report  results/authors-run.json        # markdown
```

## Definition of done for a module

1. README has all eight sections.
2. `verify.sh` exists, runs, and its gate traces to a named Success Criterion.
3. `results/authors-run.json` exists, validates, and is not a dry run.
4. The *Our numbers* section reports what actually happened, including nulls.
5. `tools/audit.sh` exits 0.

A module that fails any of these does not merge, regardless of how good the prose is.

## Known gaps

Kept current on purpose so an agent doesn't rediscover them or paper over them:

- No `verify.sh` implementations yet. M04's is specified but not written.
- No real ablation results anywhere. Every *Our numbers* section is a placeholder.
- `tools/audit.sh` is referenced throughout but not yet implemented.
- The reference agent CLI is undecided (`docs/COURSE-SPEC.md` open question 1).
- The shared capstone repo is undecided (open question 2).

If you are an agent picking up work here: these five, in this order, are the backlog.
Pick exactly one. Do not attempt two.

## What this repo is not

Not an agent framework. Not a general agentic-coding course — that space is served by
`walkinglabs/learn-harness-engineering` and we link to it rather than compete. Not
vendor-neutral theatre: labs name a specific CLI and stack, with a documented porting
contract.
