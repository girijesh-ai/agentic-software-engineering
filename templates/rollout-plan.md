# Harness rollout plan — [team / org]

One page. If it runs to three, you haven't decided anything yet.

Graded against SC-6. A plan with no stated stop-loss condition does not pass, however
good the rest of it is.

---

## 1. The first topology

Most organisations have three or four service shapes that cover 80% of what they
build. You are not harnessing "the codebase." You are harnessing one topology, then
templating it.

- **Topology chosen:** [e.g. batch training pipelines on the feature store]
- **How many repos share this shape:** [n]
- **Why this one first:** [highest agent usage / worst failure rate / most repos share
  the shape / most harnessable]
- **Harnessability honestly assessed:** what structural properties does this topology
  already have that afford sensors? Typing, module boundaries, existing test coverage,
  a runnable local environment? What is missing, and is closing that gap part of this
  plan or a prerequisite to it?

> The argument for picking a topology rather than a repo is Ashby's Law: a regulator
> needs at least as much variety as the system it governs. An agent can produce
> almost anything; committing to a topology is a deliberate variety-reduction move
> that makes a comprehensive harness achievable at all.

## 2. Baseline, taken before you change anything

You cannot claim an improvement you did not measure a "before" for. Pull these from
systems you already have.

| Metric | Current | Source | Date |
|---|---|---|---|
| Cost per merged PR | | | |
| Time-to-merge, agent-assisted work | | | |
| Rework rate (reverts, follow-up fixes within 14d) | | | |
| Review latency relative to PR size | | | |
| Compute spend per engineer | | | |

Rework rate is the honest one. Velocity metrics improve the moment you adopt agents;
rework tells you whether the improvement was real.

## 3. The first three sensors

Not thirty. Three. Each one closes a failure class you have actually observed.

| # | Failure observed | Sensor | Computational or inferential | Where it runs | Cost/run |
|---|---|---|---|---|---|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |

For each: what is the failure message the agent will see, and does it carry
remediation instructions or just a verdict?

## 4. What you are explicitly not automating

The harness externalises what an experienced engineer brings implicitly — absorbed
conventions, felt cognitive pain at complexity, social accountability, memory of which
debt is tolerated for business reasons. It only goes so far. A good harness doesn't
eliminate human input; it directs human input to where it matters most.

Name where that is on your team:

- [ ] [e.g. any change to the fairness constraint set]
- [ ] [e.g. anything touching the customer-facing scoring threshold]
- [ ] [e.g. architecture decisions that create a new module boundary]

If this list is empty, you have not thought about it hard enough.

## 5. Investment, stated as infrastructure

A harness is a second codebase. On a legacy repo with years of unwritten conventions,
the backfill is steep and ongoing. Budget it accordingly.

- **Build:** [n engineer-weeks]
- **Maintenance:** [n% of a person, ongoing — sensors rot, docs drift, someone gardens]
- **Compute:** [$/month for inferential sensors and eval tiers]
- **Who owns it:** [a named person, not "the team"]

## 6. Stop-loss

**What result would make you roll this back?**

- [ ] Rework rate has not improved by [x]% after [n] weeks
- [ ] Cost per merged PR up more than [x]% with no quality gain
- [ ] Engineers routing around the harness rather than through it (measure: [how])
- [ ] Maintenance exceeding [n] hours/week

**Review date:** [date]
**Decision owner:** [name]

An adoption plan without a stated failure condition is not a plan. It is a bet with
no exit.

## 7. What you'll report upward, and what you won't claim

- **Will report:** [the four metrics, with confidence intervals where you have them]
- **Will not claim:** [e.g. "10x productivity" — you have not measured that and the
  published 10x figure comes from a greenfield team with zero legacy constraints and
  a no-manually-written-code policy, which is not your situation]

Overclaiming early is the fastest way to lose the budget when the honest number
arrives.
