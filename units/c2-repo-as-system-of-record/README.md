# C2 · The repository is the only thing that exists

**Prerequisites.** None from the running thread - this unit's object of
study is the course repo itself, not the shared FastAPI codebase.
**Time.** ~3 hours. **Cost.** Under $10 in agent tokens.

<!-- capabilities: agent-authoring, doc-gardening -->
**Serves.** SC-7, via §4.1's sensor and §6's ablation.

---

## 1. The question

Why did your beautifully written 800-line `CLAUDE.md` make things worse?

## 2. The failure

A monolithic instruction file fails four ways, per the curriculum: it
crowds out the task, it makes everything "important" so nothing is, it
rots instantly, and it can't be mechanically checked. This repo has been
built on the opposite bet since session zero - `AGENTS.md` as a map under
120 lines, `docs/` as the system of record - without ever actually testing
whether that bet pays off, or just asserting it. And the "can't be
mechanically checked" half had a real, unexamined gap: `tools/audit.sh`
checks structure and links, but nothing checked whether the docs it
approves still describe the repo they're sitting in. Both gaps closed in
this unit; §6 has the ablation, §4.1 has the sensor - and the sensor found
a real problem on its first real run, not a seeded one.

## 3. The idea

### 3.1 What the agent can't see doesn't exist

The Slack thread that aligned a team on an architectural pattern is
invisible to an agent. So is the Google Doc, so is the thing in a staff
engineer's head. Repository-local, versioned artifacts are all an agent
actually has - which makes `docs/` the *only* place decisions can live if
they're meant to survive past the person who made them.

### 3.2 A link checker proves reachable, not current

`tools/audit.sh` check 4 already resolves every internal Markdown link in
this repo - that's the literal "link checker green" half of this unit's
gate, dogfooded since before this unit existed (§5 cites it directly rather
than rebuilding it). But a link checker's job ends at "the file exists." It
cannot tell you the file it resolved to is still true. `docs/BUILD-ORDER.md`
proved this the first time anything looked: it linked cleanly to
`tools/audit.sh` while asserting, in prose, that `tools/audit.sh` "doesn't
exist" - both statements checkable, both present in the same repo, and only
one of this course's own sensors was checking the second one.

### 3.3 A gardener checks currency, not existence

`tools/garden_docs.py` (§4.1) is the missing sensor: it looks for a doc
making a "this doesn't exist yet" or "this is a placeholder" claim about
something a link checker would confirm *does* exist, and for a stated
build-order sequence that the repo's own shipped results contradict.
Neither check is generic staleness detection (which is unbounded and would
false-positive constantly, the same trap `spec_lint.py`'s own heuristics
admit to) - both are narrow, specific, and only fire when the doc's claim
is checkably, currently false.

## 4. The lab

### 4.1 Part one - the gardener, run for real, no seeding

`tools/garden_docs.py` scans every Markdown file in the repo for two
patterns: STALE001 (an "X doesn't exist" claim naming a path that now
resolves and is non-empty) and STALE002 (a stated unit build-order chain
where a later unit has real shipped results and an earlier one in the
chain doesn't exist yet). Run against this repo's actual current state -
not a fixture built to make it fire - it found two real findings on its
first run, both in `docs/BUILD-ORDER.md`:

```
$ python3 tools/garden_docs.py
garden_docs: 2 finding(s).

  STALE001  docs/BUILD-ORDER.md:47
    line says '...Referenced in six places and doesn't exist...',
    naming 'tools/audit.sh', which exists and is non-empty now.

  STALE002  docs/BUILD-ORDER.md:87
    states the order 'c2 -> c3', but 'c3' has real shipped results
    and 'c2' does not exist yet.
```

(Full transcripts: `results/lab-materials/gardener-run-before-fix.txt` and
`...-after-existence-fix.txt`.) `docs/BUILD-ORDER.md` was a genuine
bootstrapping runbook, written before any unit had real numbers, never
revisited once the repo matured past it - exactly the "rots instantly"
failure mode this unit's §1 opens with, just in a planning doc instead of a
`CLAUDE.md`. Fixed directly (see that file's new header note and its
corrected `tools/audit.sh` line) rather than left as a permanent fixture,
because leaving a known-stale doc in the repo on purpose to keep a demo
working would be its own small instance of the same failure. The STALE002
finding on the build-order chain is left in place deliberately - it
self-clears the moment this unit ships its own real results, which is a
property of the sensor's design, not an oversight.

### 4.2 Part two - the ablation

**Step 1 - Build the monolithic file for real, from this repo's own
content.** `AGENTS.md` plus the full text of all eight docs it points to
(`COURSE-SPEC.md`, `CURRICULUM.md`, `SKILLS-MAP.md`, `PLUGIN-CONTRACT.md`,
`POSITIONING.md`, `ARCHITECTURE-AUDIT.md`, `ECOSYSTEM-MAP.md`,
`CS146S-COVERAGE.md`), concatenated into one `CLAUDE.md`: 2,456 lines, all
of it real, current content - no invented bulk. Building it surfaced a
concrete, mechanical instance of the exact failure §1 opens with, before
any agent was even involved: every one of those docs' own relative
Markdown links (`PLUGIN-CONTRACT.md`, `../tools/check_skills_map.py`, and
so on) resolves correctly from `docs/`, and every one of them silently
breaks once concatenated into a file sitting somewhere else. Cross-linking
doesn't survive being copied out of its own directory - this repo's own
link checker (`tools/audit.sh` check 4) caught it immediately, and this
unit's fix was to scope that check to skip frozen fixture snapshots under
`results/lab-materials/` (see that script's own comment), not to weaken
what it checks for live docs.

**Step 2 - Five real, verifiable comprehension tasks**, reusing B0's exact
Q&A/`check_answer.py` shape: the AGENTS.md line cap and its enforcing
script, the exact name of the "obsolete" section, SC-5's ID and its
statistical method, the spec-linting tool's name, and the "never invent a
result" rule and what must produce one instead. Each answer is a specific,
quotable fact that exists verbatim in this repo today.

**Step 3 - Ablate structure itself, content held constant.** `structured`
gets the real `AGENTS.md` and `docs/` tree, untouched. `monolithic` gets
the same information with `AGENTS.md` and `docs/` moved aside and replaced
by the one 2,456-line file - not a weaker test where the agent can route
around the monolith back to the real docs. 5 tasks x 2 arms x 3 repeats =
30 runs, `claude-haiku-4-5`, reset to a fresh clone of this repo's `main`
between every run.

## 5. The gate

```bash
./verify.sh
```

Passes when: `AGENTS.md` is ≤120 lines (checked directly - this unit's
claim is about *this* repo); `tools/audit.sh` passes (the repo-wide link
checker, cited not reimplemented); `tools/garden_docs.py` currently reports
clean; the gardener transcripts and arm materials exist; and
`results/authors-run.json` is a real run with the `structured`/`monolithic`
arms, ≥5 tasks, ≥15 runs per arm, passing `tools/ablation.py validate`
directly (SC-5's standard shape, same as C4).

## 6. Our numbers

Real run: `results/authors-run.json`, 30 runs (2 arms x 5 tasks x 3
repeats), `claude-haiku-4-5`, against the 5-task Q&A pool in § 4.2.
Verified 2026-09-21.

| Arm | n | Pass rate | Median agent wall (s) |
|---|---|---|---|
| structured | 15 | 100% | 19.5 |
| monolithic | 15 | 100% | 15.0 |

`monolithic` vs `structured`: **+0.0%** (95% CI 0 to 0) - a perfect
ceiling, every one of 30 runs found the right fact regardless of arm. Per
task, all five hit 100% in both arms - no exceptions to round off.

**A dead-even pass rate does not mean the two conditions were
indistinguishable.** Wall-clock time was: structured's median (19.5s) is
30% slower than monolithic's (15.0s), and structured's slowest run (51.0s)
took over twice as long as monolithic's slowest (23.0s). Reading a
`monolithic` transcript directly (§4.2's `agents-md-limit` task, 15.5s
wall) shows why: one search across the single file finds both required
facts in the same pass. A `structured` run has to first open `AGENTS.md`,
then decide whether the answer is there or needs a follow-up read into
`docs/`, then possibly make that second read - more tool round-trips for
the same fact, even when the first guess is right.

**Why the pass rate itself says nothing about the curriculum's actual
claim.** The four failure modes §2 opens with - crowds out the task, makes
everything "important" so nothing is, rots instantly, can't be mechanically
checked - are about a monolithic file at the point it exceeds what a reader
(human or model) can hold as signal, or when it contains many competing,
nuanced, or conflicting instructions the agent must weigh. A single
correct fact, findable by one search term, in a 2,456-line file that still
fits comfortably in context, tests none of that. This ablation shows a
capable model's information-retrieval floor doesn't care about file
count - which is a real, useful, and different finding from "monolithic
files are fine," and worth being precise about which one this is.

**Limitations, stated plainly:**

1. **This measures lookup, not judgment.** All five tasks have one
   objectively correct, quotable answer. The curriculum's stronger claim -
   that a monolithic file makes "everything important so nothing is" -
   is about competing signals crowding a decision, not about locating one
   fact. A task requiring the agent to *reconcile* two documents that
   partially conflict, or to prioritize among many stated rules, is the
   ablation that would actually test that claim, and it isn't this one.
2. **2,456 lines never approached a real context-budget problem** for a
   model with a context window in the hundreds of thousands of tokens.
   "Rots instantly" and "crowds out the task" are claims about scale this
   unit's fixture doesn't reach - a monolith assembled from a much larger
   real docs tree, or a genuinely long-running session where the file
   competes with a large accumulated transcript, might behave differently.
3. **n=3 per (arm, task) cell**, though a perfect 30/30 result is not the
   kind of finding a wider confidence interval would plausibly overturn -
   the ceiling itself, not its precision, is the finding.

## 7. What makes this obsolete

The direct next step is named in §6's limitations: this unit tested
lookup, not judgment. The ablation that would actually test the
curriculum's stronger claim gives both arms a task requiring the agent to
reconcile two partially-conflicting stated rules, or prioritize among many,
rather than locate one fact - that's where "everything important so
nothing is" should bite, if it bites at all, and it's a materially
different experiment from this one. Separately: if a future harness gives
every session a persistent, queryable index over the whole repo regardless
of what's in `CLAUDE.md`, the monolithic-vs-structured distinction stops
mattering for retrieval tasks specifically - the failure mode moves from
"can't find it" to "the index is wrong." And `garden_docs.py` is
deliberately narrow (two specific claim shapes); a more general staleness
detector - one that catches drift in prose claims, not just existence and
sequence claims - is real future work, named rather than attempted here,
per `spec_lint.py`'s own precedent of staying narrow and named rather than
chasing full generality.

## 8. Sources

- `docs/CURRICULUM.md` § C2 - the monolithic-file failure modes and the
  three-part gate this unit's `verify.sh` checks.
- `docs/COURSE-SPEC.md` SC-7 - "the repo is its own worked example," the
  criterion this entire unit is built to satisfy about itself.
- `docs/BUILD-ORDER.md` - the real stale doc `tools/garden_docs.py` found,
  before and after this unit's fix.
- `units/b0-onboarding-a-codebase/README.md` § 4 and its
  `check_answer.py` - the Q&A/verifier shape this unit's ablation reuses
  unchanged.
- `units/c4-spec-as-sensor/README.md` § 6 - the prior unit whose ablation
  shape (N≥5 tasks, `ablation.py validate` passing directly) this unit's
  gate matches.
