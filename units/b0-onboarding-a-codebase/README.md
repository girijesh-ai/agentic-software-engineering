# B0 · Onboarding an agent to a codebase you didn't write

**Prerequisites.** None — this is the first unit in Track B and picks the running
thread the rest of Track B and C build on.
**Time.** ~2 hours. **Cost.** Under $5 in agent tokens.

<!-- capabilities: repo-mapping, load-bearing-convention-analysis, history-mining -->
**Serves.** SC-5. Also the unit that starts the running thread SC-11 depends on.

---

## 1. The question

The repo is 400k lines. The context window is not.

## 2. The failure

Every other unit in this course assumes a repo you can hold in your head, or at least
in one context window. This one runs against the opposite case: a real, unfamiliar
codebase, and everything below is a friction point the author actually hit building
this unit's own lab and B1's ablation against
[`tiangolo/full-stack-fastapi-template`](https://github.com/tiangolo/full-stack-fastapi-template)
— not a constructed example.

| What happened | Why nothing caught it |
|---|---|
| Ran `pytest` directly in a fresh checkout. Every test failed at import, before any test logic ran. | The repo's own README doesn't mention it; only `scripts/test.sh` sets `FASTAPI_ENV=development`, silently, and nothing fails loudly if you skip that script and call pytest yourself. |
| Assumed resetting the git working tree (`git checkout . && git clean -fd`) fully reset state between two runs of the same task. | `alembic_version` lives in a row in Postgres, not a file. A migration applied in run 1 stayed applied in run 2's database even after the migration's own `.py` file was deleted, and the next `alembic upgrade head` failed looking for a revision that no longer existed on disk. |
| Wrote a test asserting a specific ORM field name (`is_archived`) for an "archive instead of delete" feature. | The ticket never specified a field name. A different, equally correct implementation (`archived_at: datetime | None`) failed the test not because the code was wrong, but because the test checked an implementation detail nobody had agreed on. |
| Deleted a stray Alembic migration file with `git clean -fd`, then re-ran the same task and hit a phantom-revision error again. | `__pycache__/` is gitignored, so `git clean -fd` (without `-x`) never touches it, and a `.pyc` from the deleted migration lingered where a later step could still reference it. |

None of these are model failures. Each is a fact about *this specific repo* that
lives nowhere a fresh context window would find it without being told, or without
paying to rediscover it by trial and error. That rediscovery cost is the thing a map
is supposed to buy back.

## 3. The idea

### 3.1 A map is not documentation

A README describes what the project is for. A map for an agent answers a narrower,
more mechanical question: *given a task, where do I start reading, and what will
silently break if I don't know X?* Those are different documents with different
audiences, and conflating them is why a project's own README is often useless for
this purpose even when it's well written — it wasn't optimized for this question.

### 3.2 Build the map before the harness

You cannot design good sensors (Track C) for conventions you haven't identified yet.
A linter that enforces "every item route checks ownership" only occurs to you once
you've noticed that the check is inline and repeated rather than centralized — which
is exactly the kind of fact §2's table is full of. Skipping straight to tooling on an
unfamiliar repo means building sensors for the conventions you happened to notice,
which is a biased and usually incomplete sample.

### 3.3 Load-bearing versus habit

Not everything consistent in a codebase is required. Gitmoji commit prefixes are
consistent in the running-thread repo and enforce nothing. `FASTAPI_ENV=development`
being set is inconsistent in visibility (one script sets it, nothing else mentions
it) and breaks every test if missed. Consistency is not the signal; *what actually
fails, and how loudly, when you deviate* is the signal. This is a judgment call, not
a lint rule — `engineering-standards` can tell you a convention exists, not whether
violating it costs you an hour or a production incident.

### 3.4 Reading history as evidence, not archaeology

`git log` filtered for maintainer-authored, non-bot, non-release commits is a record
of decisions, not just changes. In the running-thread repo, three separate commits
independently titled "Simplify..." are a trend, not a coincidence, and a trend is
evidence about which direction new work should go. This is cheap to check and easy
to skip, which is exactly why it's worth stating as a deliberate lab step rather than
something you'll get to if there's time.

### 3.5 The honest budget

This repo is roughly 1500 commits and two applications. The map in this unit's lab
took a directory listing, an unshallowed `git log`, three config files, and one
reproduced error — a few hours, most of it already paid for while building B1. At
400k lines, the same directory-listing-and-grep technique does not scale, and this
unit does not claim it does. What should scale — sampling entry points, reading
history for trend rather than completeness, treating the map as a living artifact
with its own freshness check — is exactly what the "obsolete when" note below is
about.

## 4. The lab

**Step 1 — Pick the running thread (done for this unit).** Repo:
`tiangolo/full-stack-fastapi-template`. Feature: team-based item sharing with roles
(owner/editor/viewer), replacing today's single-owner model. Picked here because it's
substantial enough to carry meaningfully through B1 (real spec ambiguity: what can a
viewer do?), B2 (real planning surface), B3 (easy to under- or over-build), B4 (real
reviewable surface), and because it touches the one fact §2 and the map both surface:
permission checks are inline per-handler, not centralized, so adding roles is either a
mechanical repetition of the same check five times or a real refactor decision made
up front.

**Step 2 — Produce the map (done for this unit).**
[`repo-map.md`](results/lab-materials/repo-map.md) — structure, entry points by task
kind, and the permission/generated-client facts from §2.
[`load-bearing.md`](results/lab-materials/load-bearing.md) — the load-bearing-vs-habit
table from §3.3, plus the honest budget note.

**Step 3 — Write five locate tasks against facts the map states (done for this unit).**
Each has a single verifiable answer, checked by
[`check_answer.py`](results/lab-materials/check_answer.py) against required terms in
an `ANSWER.md` the agent writes — a comprehension task, not a code-diff task, so the
verifier is schema-agnostic text matching rather than a pytest suite:

| Task | What it asks | What the answer must contain |
|---|---|---|
| `permission-location` | Where is item read/write permission decided? | `items.py`, and `owner_id` or `is_superuser` |
| `client-generation` | Where does the frontend API client come from? | `generate` (or `generated`), and `openapi` |
| `migration-mechanism` | How does a new model field reach the live database? | `alembic`, `migration` |
| `test-env-gotcha` | Why does `pytest` fail immediately in a bare checkout? | `FASTAPI_ENV`, `development` |
| `db-url-history` | Was the Postgres connection always one `DATABASE_URL`? | `DATABASE_URL`, evidence of a prior/different form |

**Step 4 — Ablate: same five tasks, with and without the map (this unit's own gate
data).** Arm A gets a bare prompt and a fresh checkout. Arm B gets the same prompt
plus `repo-map.md` and `load-bearing.md` placed in the repo and a `CLAUDE.md` pointing
to them. `tools/ablation.py`, 5 tasks × 4 repeats, two arms.

## 5. The gate

```bash
./verify.sh
```

Passes when: the map and load-bearing note exist and are non-empty;
`results/authors-run.json` validates (`tools/ablation.py validate`), is not a dry run,
has both arms present across all five tasks; and the with-map arm answers correctly on
at least 3 of its 4 attempts on every task (the gate's own bar, stricter per-task than
the aggregate ablation comparison).

Traced to **SC-5** in [`docs/COURSE-SPEC.md`](../../docs/COURSE-SPEC.md) — this gate
*is* an N≥5×K≥3, two-arm, bootstrap-CI measurement of a harness change, which is
exactly SC-5's eval shape.

## 6. Our numbers

Real run: `results/authors-run.json`, 40 invocations (2 arms × 5 tasks × 4 repeats),
`claude-haiku-4-5`, against a fresh clone of
[`tiangolo/full-stack-fastapi-template`](https://github.com/tiangolo/full-stack-fastapi-template)
reset between every run. Verified 2026-09-08.

| Arm | Pass rate | Median agent wall (s) |
|---|---|---|
| No map | 95% (19/20) | 60.4 |
| With map | 100% (20/20) | 39.5 |

`with-map` vs `no-map` pass rate: **+5.0pp** (95% CI +0.000 to +0.150 — inconclusive,
interval crosses zero). Per task, four of five hit 100% in *both* arms; the only gap
was `test-env-gotcha` at 75% without the map. n=4 per (arm, task) cell; a near-ceiling
result here is a real finding, not a shortfall in the ablation.

**The gate passed, but pass rate is the wrong column to look at.** At this task
difficulty and this model, a competent agent finds most of these facts unprompted by
just reading the error or grepping the right file — the map didn't need to *enable*
correctness here, because the baseline wasn't struggling much to begin with. That's
worth saying plainly rather than reaching for the map's benefit anyway.

**Wall-clock time is where the effect actually is.** Median time dropped 60.4s → 39.5s.
Run through the same bootstrap procedure `tools/ablation.py` uses for pass rate (not
built into the tool's own report, computed separately for this write-up): 95% CI on the
wall-time delta is **-41.4s to -3.8s** — excludes zero, a real effect. The map's value
in this run was speed, not correctness: an agent that already tends to find the right
answer finds it faster when it doesn't have to rediscover the codebase's shape from
scratch each time.

**A genuine harness bug, not a finding, briefly produced a fake 0%.** The
`db-url-history` verifier used a pipe-separated OR syntax (`separate|2184|migrat`)
unquoted in the shell command string; the shell read the pipes as actual pipes to
non-existent commands, so the checker never ran, and every one of 4 real, correct
answers scored as a failure. Caught by reading the transcripts before trusting the
number, not by any automated check — worth stating because it is exactly the kind of
silent, plausible-looking wrong number this course's core commitments exist to catch,
and this time a person had to catch it by hand.

## 7. What makes this obsolete

The curriculum flags this directly: **cheap, effective context over an entire repo
would retire this unit**, and it may go before anything else in Track B. If a model
can hold a 400k-line repo's load-bearing structure in context reliably and cheaply,
the map is redundant with what the model already does for free, and the lab becomes
"describe what you already have," which is not a lab.

Short of that: any technique that makes maps self-maintaining (regenerated from a
repo's own structure and history on a schedule, rather than hand-written once) would
obsolete the *hand-written* version specifically, while keeping the underlying claim
— onboarding needs an artifact, not just a bigger window — intact.

## 8. Sources

- `docs/ARCHITECTURE-AUDIT.md` § F3 — the greenfield-bias finding this unit exists
  to close.
- `docs/CURRICULUM.md` § The running thread — why one repo and one feature carry
  through eleven units.
- Direct exploration of `tiangolo/full-stack-fastapi-template`: `git log`,
  `.pre-commit-config.yaml`, `CONTRIBUTING.md`, `compose.yml` — this unit's own
  primary source, cited inline in `repo-map.md` and `load-bearing.md`.
