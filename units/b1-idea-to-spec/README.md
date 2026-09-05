# B1 · Idea → spec

> Reference unit. This is the shape and depth every other unit must hit.

**Prerequisites.** A2 (you can name your harness's configuration points), A3 (you've
reproduced the context failure modes).
**Time.** ~3 hours. **Cost.** Under $5 in agent tokens.

<!-- capabilities: issue-intake, domain-vocabulary, spec-authoring, spec-pressure-test, spec-linting -->
**Serves.** SC-2, SC-3.

---

## 1. The question

Which agent failures can no sensor catch?

## 2. The failure

Do this before reading further, on a real ticket from your own backlog.

Give an agent a normally-worded task — the kind you'd give a competent contractor —
and let it run to a PR without interrupting. Something like *"add rate limiting to the
public API."*

Now read the diff properly. In our runs, the four failures that showed up were not the
ones people expect:

| What happened | Why nothing caught it |
|---|---|
| Correct, tested, well-structured token-bucket limiter. Per-process. You run twelve pods. | Every test passed. Every lint passed. Nobody said "distributed." |
| Rate limited by IP. Half your traffic is behind one corporate NAT. | The requirement "per customer" existed only in your head. |
| Built a full quota-management subsystem with an admin UI. | You asked for rate limiting. It inferred the rest, plausibly. |
| Correct implementation of the thing you asked for. You asked for the wrong thing. | No instrument in the system was pointed at that question. |

None of these is a code quality failure. The code is fine. Tests are green. A reviewer
skimming the diff would approve it.

This is the failure class that actually burns teams, and it has a precise name:
**well-formed code that solves the wrong problem.**

## 3. The idea

### 3.1 The sensor gap

Track C will teach you to build sensors. Before you get excited about them, understand
what they can't do.

Computational sensors — tests, linters, type checkers, structural analysis — catch
structural problems reliably and cheaply: duplication, cyclomatic complexity, missing
coverage, architectural drift, style violations. Deterministic, proven, run on every
change.

Inferential sensors — AI review, LLM-as-judge — partially catch problems needing
semantic judgment: semantically duplicated code, redundant tests, brute-force fixes,
over-engineering. Expensively and probabilistically. Not on every commit.

**Neither reliably catches misdiagnosis of the problem, unnecessary features, or
misunderstood instructions.** They'll sometimes catch them. Not reliably enough to
reduce supervision.

Böckeler states the consequence plainly: correctness is outside every sensor's remit if
the human didn't clearly specify what they wanted in the first place. You cannot build
your way out of this with better tooling. There is exactly one instrument that detects
wrong-problem failures, and it is a written statement of the right problem.

That statement is the **behaviour harness**. Everything else in the harness regulates
maintainability and architecture fitness. Only the spec regulates behaviour.

### 3.2 The prompt is the new source code, and you keep throwing it away

Normally you keep the human-readable source and discard the machine-readable binary.
With agents, teams do the opposite: they craft a detailed prompt — the specification —
generate code from it, commit the code, and throw the prompt away.

That is shredding the source and version-controlling the binary.

**The generated code is a lossy projection of the specification.** The intent, the
business logic, the constraints that were considered and rejected, the reason the
threshold is 0.7 — none of it survives the projection. Six weeks later, another agent
reads only the projection and re-derives intent from artifacts that never contained it.

The practical rule: specs are versioned, reviewed and diffed with the same discipline as
source. In this course they live in the repo, they're linted in CI, and `review-code`
checks the diff against them.

### 3.3 What makes a Success Criterion actually measurable

Most specs fail here, and they fail in a consistent way. Compare:

```
❌  The API should handle high load gracefully.
❌  Rate limiting should be robust and shouldn't impact legitimate users.
❌  Improve the performance of the feature pipeline.
```

Each sounds like a requirement. None of them can be wrong. An agent reading these has
been given permission to decide what "graceful," "robust" and "improve" mean, and it
will decide generously — in its own favour, at the moment it's tired of the task.

The same intent, specified:

```
✅  SC-1 — A single customer exceeding 100 req/min receives HTTP 429 with a
    Retry-After header, and other customers' p99 latency is unchanged.
    Eval: tests/test_rate_limit.py::test_isolation — one customer floods,
    second customer's p99 stays within 5% of its unloaded baseline.

✅  SC-2 — Limits hold across all replicas, not per-process.
    Eval: tests/test_rate_limit.py::test_distributed — 3 app instances behind
    the fixture LB, one customer at 150 req/min total, exactly 100 succeed.

✅  SC-3 — Rate limit state loss does not fail requests open.
    Eval: tests/test_rate_limit.py::test_backend_down — kill the store,
    assert requests are rejected, not silently unlimited.
```

Three properties make the difference:

1. **A falsifiable statement.** Someone can say "no, that's not true."
2. **A named eval.** Not "we'll test it" — the actual identifier of the thing that
   decides. If the eval doesn't exist yet, the criterion is a wish.
3. **A number where a number is possible.** "Unchanged" becomes "within 5%."

The third one has a trap. Precision you can't justify is worse than a stated range,
because it looks like evidence. If you don't know the right p99 budget, write the range
you'd accept and say why, rather than inventing 200ms because it's round.

SC-3 is the one most specs miss. Success criteria describe what happens when it works;
the expensive failures are in the unstated behaviour when it doesn't. `grill-me` exists
mostly to find these.

### 3.4 The spec is where you decide, not where you record having decided

`spec-from-idea` produces two to three approaches before it produces a spec, and the
temptation is to skim that section. Don't. It's where the leverage is.

An agent handed a spec with one approach will implement it. An agent handed a problem
with three considered approaches and a stated reason for the choice will *recognise*
when the reason stops holding mid-implementation — because it has the reason. This is
also the artifact that answers the question a future maintainer actually asks, which is
never "what does this do" but always "why is it like this."

Record the rejected approaches. Rejected options are the cheapest documentation you will
ever write and the only kind that stops the same debate recurring every quarter.

### 3.5 Domain vocabulary is load-bearing

`domain-modeling` looks like a nicety. It isn't.

If "customer" means the billing account in one part of your system and the API key in
another, then a spec saying "per customer" is ambiguous, and the agent will pick one
consistently, plausibly, and wrongly, and every downstream test will confirm its
choice. Ambiguity in the spec's vocabulary doesn't produce an error. It produces
confident, coherent, wrong software.

Run `domain-modeling` *before* `spec-from-idea` when the domain terms are contested.
The output is a paragraph. It prevents a class of failure that costs weeks.

## 4. The lab

**Step 0 — Install the plugin (5 min).**

```bash
claude plugin marketplace add girijesh-ai/spec-driven-engineering
claude plugin install spec-driven-engineering@spec-driven-engineering-dev
```

**Step 1 — Reproduce the failure (30 min).**
Run §2 on a real backlog item. Save the diff and your findings. This is your baseline
arm — do not skip it, because §6 needs it.

**Step 2 — Triage the ticket (15 min).**
Invoke `triage-issues` on the same item. Most bad specs start as unexamined tickets;
notice what triage surfaces that the ticket didn't say.

**Step 3 — Fix the vocabulary (15 min).**
Invoke `domain-modeling` if any term in the ticket is contested. Write down which term
was ambiguous and what you decided it means.

**Step 4 — Write the spec (45 min).**
Invoke `spec-from-idea`. Push back on it. Aim for 3–6 Success Criteria, each with a
named eval, each falsifiable. Include at least one negative criterion — what must
happen when the thing fails.

**Step 5 — Lint it (10 min).**

```bash
python3 tools/spec_lint.py specs/your-spec.md
```

Fix what it flags. Read the failure messages carefully: they're written in the style
C3 teaches, carrying remediation rather than a verdict. This is the first time in the
course you're on the receiving end of a sensor built the right way.

**Step 6 — Pressure-test it (20 min).**
Invoke `grill-me`. It exists to find the criterion you didn't write. Add what it finds.
Re-lint.

**Step 7 — Measure (30 min).**
Re-run the same task with the spec as a guide. Record both arms with
`tools/ablation.py`.

## 5. The gate

```bash
./verify.sh
```

Passes when: `spec_lint` exits 0 on your spec; every Success Criterion names an eval
that exists or is explicitly marked as not-yet-written; at least one criterion covers
failure behaviour; and `results/learner-run.json` validates with both arms present.

Traced to **SC-2** and **SC-3** in [`docs/COURSE-SPEC.md`](../../docs/COURSE-SPEC.md).

## 6. Our numbers

> Placeholder. Must be filled with a real `results/authors-run.json` before this unit
> ships — CI enforces it, per SC-6. Do not publish invented numbers; the credibility of
> the course rests on this section being honest.

Planned reporting shape, four arms:

| Arm | Pass rate | Median turns | Wrong-problem failures | Cost/task |
|---|---|---|---|---|
| Bare prompt | — | — | — | — |
| Prompt + `CLAUDE.md` only | — | — | — | — |
| Spec, unlinted | — | — | — | — |
| Spec, linted + grilled | — | — | — | — |

The column that matters is *wrong-problem failures*, and it needs a human grader,
because by construction no automated check catches them — that's the unit's thesis.
Grading protocol goes in `results/README.md`: two independent graders, published
disagreement rate.

Our hypothesis is that pass rate barely separates arms two and three, while
wrong-problem failures separate them sharply. If the data disagrees, the data wins and
this unit gets rewritten.

## 7. What makes this obsolete

Almost nothing here, and that's unusual for this course.

Most harness techniques are heuristics engineered around current model failures and
will retire as models improve. LangChain says so about their own loop detection. Track
C is full of scaffolding with a shelf life.

The spec is the opposite. As models get better at execution, the bottleneck moves
*further* toward specification, not away from it. A model that implements anything
correctly still cannot know which thing you wanted. Deciding what "good" means and
writing it down is the part of engineering that doesn't automate, and every capability
gain makes it a larger fraction of the remaining work.

The tooling around it will change. `spec_lint` will get better. Agents will draft
better first-pass specs and interrogate them harder. What won't change is that someone
has to hold the falsifiable statement of intent, and that someone is accountable in a
way an agent isn't.

## 8. Sources

- Böckeler / Thoughtworks — *Harness engineering for coding agent users* (guides and
  sensors; the categories of failure neither catches; the behaviour harness as the open
  problem)
- Stanford CS146S — *The Modern Software Developer* (the prompt as source code; the
  generated code as lossy projection)
- OpenAI — *Harness engineering: leveraging Codex in an agent-first world* (plans and
  specs as first-class versioned repository artifacts)
- Anthropic — *Effective harnesses for long-running agents* (feature lists as
  machine-readable scope; premature completion)
- `spec-driven-engineering` — `spec-from-idea`, `domain-modeling`, `grill-me`,
  `triage-issues`
