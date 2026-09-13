# B3 · Plan → code

**Prerequisites.** B2 (you have a plan whose steps trace to a spec).
**Time.** ~3 hours. **Cost.** Under $5 in agent tokens.

<!-- capabilities: implementation-loop, test-first, code-standards, systematic-debugging -->
**Serves.** SC-6.

---

## 1. The question

What does test-first mean when the agent writes both the test and the code?

## 2. The failure

Test-first is supposed to work because the test is written by someone who
understands the requirement *before* they've committed to an implementation - the
test encodes the requirement, independent of whatever code eventually satisfies it.
That independence is the whole mechanism. It disappears the moment the same agent,
in the same turn, writes both.

This unit's own ablation (§6) makes the failure concrete rather than hypothetical.
Every one of 13 self-tested runs that produced a test suite scored a **perfect 1.00
mutation score** - the tests caught every single artificial bug introduced into the
agent's own code. And a third of those same runs failed the *actual* spec's hidden
acceptance test. The tests were not weak. They were strong evidence for the wrong
claim: that the code does what the agent decided to build, which is a different
statement from does the code do what was asked. A perfect test suite and a wrong
implementation are not in tension when the same misunderstanding produced both.

## 3. The idea

### 3.1 Mutation testing measures the wrong half of the problem

Mutate a line, rerun the tests, see if something fails - that's the mechanism, and
it genuinely tells you whether a test suite is *internally* connected to the code it
guards. What it cannot tell you is whether the pair of them, code and test together,
agrees with a requirement that lives outside both. §6's data is the sharpest
statement of this available: mutation score was 1.00 whether or not the
implementation was correct. As a sensor for "is this test suite worth trusting,"
it has a blind spot exactly the shape of this unit's own thesis.

### 3.2 Test-first only works when the test comes from somewhere else

The actual mechanism that closed the gap in this unit's ablation wasn't "tests
exist" - the self-tested arm had tests too, and excellent ones by the mutation
metric. It was that the `test-first` arm's test came from B1/B2's spec, written
independently of the implementation, before an agent ever saw the ticket. Test-first
is a claim about *where the test's authority comes from*, not a claim about whether
a test exists at the time code is written.

### 3.3 The enforcement lesson

`superpowers`' TDD skill deletes code written before a failing test exists. Most TDD
skills, including anything this course would ship, ask nicely instead. That's the
guide/sensor distinction arriving early: a rule an agent can route around is a
guide; a rule that deletes the work is a sensor. This unit doesn't build the harder
version - noting the gap is more honest than claiming a guide is a sensor because it
sounds like one.

### 3.4 Debugging when the agent is confidently wrong

Every self-tested run that failed still reported success in its own closing
message (see §6's transcripts) - the agent had no signal it had solved an adjacent
problem, because its own tests, by construction, agreed with it. This is the
characteristic failure of agentic debugging: a plausible root cause offered with no
indication it was guessed. `debug-systematically` exists for exactly this gap, and
this unit's own data is a clean illustration of why refusing an unfalsified cause
matters more than it sounds like it should.

## 4. The lab

**Step 1 — Build the reference implementation (done for this unit).**
[`reference-implementation/`](results/lab-materials/reference-implementation/):
B2's plan, all six steps, test-first against the pre-written acceptance tests. All
nine of B2's Success Criteria pass. This is what "test-first done right" produces,
and it's the artifact B4 reviews next.

**Step 2 — Build the mutation tester.**
[`mutate_and_test.py`](results/lab-materials/mutate_and_test.py): AST-based,
standard library only - flips comparison operators, boolean constants, and
`and`/`or`, reruns a given test command per mutant, reports kill rate. Self-tested
against a deliberately weak test (confirmed it reports 0.00) and a strong one
(confirmed 1.00) before trusting it against real runs.

**Step 3 — Ablate: does the agent get worse when it must invent its own
acceptance criteria, not just write more code?** Reused B1's five tasks. Arm A
(`test-first`): the pre-written reference test is visible; implement against it.
Arm B (`self-tested`): the reference test is hidden from the working tree entirely
(not just unmentioned - physically removed before the agent's turn, restored only
for grading afterward) and the agent is told to write its own tests. Both arms get
the same one-line ticket.

## 5. The gate

```bash
./verify.sh
```

Passes when: the reference implementation exists (all six plan steps present);
`results/authors-run.json` validates (`tools/ablation.py validate`), not a dry run.

Traced to **SC-6** in [`docs/COURSE-SPEC.md`](../../docs/COURSE-SPEC.md) - the
every-unit-survives-a-number requirement, satisfied here by the ablation in §6, not
by a mutation-score bar on any single suite (§3.1 says why that bar wouldn't
discriminate anything).

## 6. Our numbers

Real run: `results/authors-run.json`, 30 invocations (2 arms × 5 tasks × 3 repeats),
`claude-haiku-4-5`, against the same `tiangolo/full-stack-fastapi-template` clone and
five tasks B1 and B2 used. Verified 2026-09-13.

| Arm | Pass rate | Median agent wall (s) |
|---|---|---|
| Test-first (reference test given) | 93% (14/15) | 63.4 |
| Self-tested (writes own code + tests) | 53% (8/15) | 129.4 |

`self-tested` vs `test-first`: **-40.0pp** (95% CI -0.667 to -0.133 — **effect
detected**, interval excludes zero). This is real, not noise: writing your own
acceptance criteria costs correctness, not just time (self-tested also took roughly
twice as long per run).

**The mutation-score result is the sharper finding.** Of the self-tested runs that
produced a test file (13 of 15 - the other 2 had no app changes to mutate), every
single one scored a perfect 1.00 - full marks whether or not the underlying
implementation matched the actual spec:

| Task | Correctness (hidden test) | Mutation score (own tests) |
|---|---|---|
| items-search | 0% (0/3) | 1.00, 1.00, 1.00 |
| items-archive | 33% (1/3) | 1.00, 1.00, 1.00 |
| login-rate-limit | 100% (1/1 with tests) | 1.00 |
| items-count | 67% (2/3) | 1.00, 1.00, 1.00 |
| protect-user-deletion | 67% (2/3) | 1.00, 1.00, 1.00 |

**This falsifies the naive version of this unit's own opening thesis.** "Mutation
test the agent's own suite" was the pre-registered answer to "how do you catch a
weak self-written test suite." The data says mutation score doesn't move with
correctness at all here - it's measuring internal consistency (does the test
suite notice when the code changes), which an agent produces reliably regardless of
whether the code is right. The real gap §3.1-§3.2 name - test authority has to come
from outside the loop that writes the code - isn't a gap mutation testing was ever
positioned to close, and this unit's plan said it was before the data came back.

One qualitative pattern worth naming directly: reading the failing self-tested
transcripts, every one reported success in its own closing summary. No run
surfaced uncertainty about whether it had solved the actual ticket - the confidently
wrong pattern §3.4 names, observed rather than assumed.

## 7. What makes this obsolete

If a model develops a reliable internal sense of "did I just satisfy the letter of
my own test or the actual ask" - something closer to noticing its own
rationalization - both halves of this unit's finding date at once: self-tested
correctness stops trailing test-first, and mutation score stops being uniformly
uninformative because a model that catches its own misreadings produces tests that
would catch someone else's too. Nothing in the current data suggests this is close;
worth re-running this exact ablation whenever a materially more capable model is the
default, since it's cheap to repeat and the result would be a real signal either way.

## 8. Sources

- `docs/CURRICULUM.md` § B3 — the mutation-testing-as-answer framing this unit's
  own data revises.
- `units/b2-spec-to-plan/results/lab-materials/spec-team-sharing.md` and
  `plan-team-sharing.md` — the spec and plan this unit's reference implementation
  builds from.
- `units/b1-idea-to-spec/README.md` — the sensor-gap thesis this unit's mutation
  result is a second, sharper instance of.
- Direct construction and self-test of `mutate_and_test.py` against known
  strong/weak test suites before trusting it against real ablation data.
