# Plugin contract

The course depends on a plugin that is still moving.
[`spec-driven-engineering`](https://github.com/girijesh-ai/spec-driven-engineering)
is at v1 with 16 skills, all marked stable, and it will grow — the course's own
[gap analysis](SKILLS-MAP.md#gap-analysis) already names five capabilities it's
missing.

A course that hard-codes skill names into twenty unit READMEs rots on the first rename.
This file is how we avoid that, and the mechanism is the same one the course teaches:
don't rely on discipline where you can rely on a sensor.

---

## 1. Units reference capabilities, not skill names

A unit teaches a *capability* — "turn an idea into a spec with measurable success
criteria." Which skill provides that capability is a binding, and bindings change.

Every unit README carries a machine-readable declaration:

```html
<!-- capabilities: spec-authoring, domain-vocabulary, spec-pressure-test, issue-intake -->
```

Invisible when rendered, parseable by CI. Prose may name the current skill for
concreteness — `spec-from-idea` reads better than "the spec-authoring capability" — but
prose is not the contract. The comment is.

**The single binding site is [`skills.lock.json`](../skills.lock.json).** When the
plugin renames `spec-from-idea`, one line in one file changes and every unit stays
correct. When the plugin *splits* a skill in two, the capability may now map to two
skills, and only the lock file knows.

## 2. The lock file pins what we tested against

```json
{
  "plugin": "spec-driven-engineering",
  "tested_against": "1.0.1",
  "capabilities": {
    "spec-authoring": {"skills": ["spec-from-idea"], "units": ["b1"]}
  }
}
```

`tested_against` is a claim with a date behind it: the units were run against that
version. If a learner installs a newer plugin, the course still works — but we haven't
verified it, and the honest move is to say so rather than imply currency we don't have.

`tools/check_skills_map.py` compares the lock file against an actual plugin checkout and
reports four conditions, each with a different meaning:

| Condition | Severity | What it means |
|---|---|---|
| Capability declared in a unit, absent from the lock | error | Broken reference. The unit teaches something nothing provides. |
| Skill in the lock, absent from the plugin | error | Renamed, removed, or the pin is stale. Course is wrong. |
| Skill in the plugin, absent from the lock | **info** | The plugin grew. Intake needed — see §3. |
| `tested_against` differs from the plugin's version | warning | Re-verify, then bump the pin. |

The third row is the interesting one, and it's why the tool exists. A new skill is not
an error; it's a signal that the course has fallen behind its own tooling. Silence there
would be the failure mode C4 warns about — a sensor that never fires because it isn't
pointed at anything.

## 3. Intake: the plugin gains a skill

Run `check_skills_map.py`, see the unmapped skill, then answer three questions in a PR.

**1. Is this a new capability, or a better implementation of one we teach?**

A better implementation is a lock-file edit. Nothing else moves. If `spec-from-idea`
gains an interview mode, `spec-authoring` still points at it and B1's prose gets a
sentence.

A new capability needs a home, which is question 2.

**2. Does an existing unit gain a lab step, or does this need a unit?**

Default is a lab step. A new unit costs a reader thirty minutes and costs us the eight
required sections, a `verify.sh`, and an ablation. That price should be paid only when
the capability represents a distinct failure mode a reader wouldn't otherwise
understand.

Test: can you write *The failure* section — a real, reproducible agent failure this
capability addresses — without straining? If not, it's a lab step in an existing unit.

**3. Does it change what the course claims?**

Two of the five gap-list skills would. `lint-spec` moving into the plugin means C4 no
longer teaches building the sensor from scratch; it teaches wiring and calibrating one.
`write-sensor` moving in means C3's lab changes shape.

That's a feature, not churn. The course is an eval for the plugin: units are where you
find out that `engineering-standards` states rules nothing enforces, or that
`spec-from-idea` produces criteria nothing checks. When a unit's existence stops being
justified because the plugin absorbed the work, **delete the unit and say so in the
changelog**. A course that only grows is a course nobody finished.

## 4. Deprecation

The plugin's rule is that a renamed skill keeps its old name working for one release
cycle as a pointer. The course's rule is stricter, because our readers are slower than
our CI: **the lock file keeps the old binding for two cycles**, marked `deprecated`, and
`check_skills_map.py` warns on every one.

```json
"spec-authoring": {
  "skills": ["author-spec"],
  "deprecated_skills": ["spec-from-idea"],
  "deprecated_until": "2027-03-01",
  "units": ["b1"]
}
```

A learner three months behind should hit a warning, not a wall.

## 5. The boundary: what belongs in the plugin, what belongs here

This is the rule that stops the course from growing a shadow skill set, which is the
most likely way both artifacts get worse.

**Belongs in the plugin.** Anything an engineer invokes to do work. Repeatable,
portable across repos, useful without having read a word of the course.

**Belongs in the course.** Anything you need to *understand* rather than invoke:
diagnostic knowledge (the context failure modes), vocabulary (guides and sensors),
methodology (ablation design), judgment (which topology to harness first), and anything
irreducibly repo-specific — a custom linter for your layer graph can't be a generic
skill.

**Belongs in neither.** Tooling that is generic but not a workflow step: `spec_lint.py`
and `ablation.py` live in `tools/`. If `lint-spec` becomes a plugin skill, the tool
stays here and the skill wraps it — one implementation, two entry points.

When something is genuinely ambiguous, prefer the plugin. It has evals, promotion gates
and a version; the course has prose.

## 6. Growth scenarios, and what each costs

| The plugin... | Course cost | Who notices |
|---|---|---|
| adds a skill covering a taught capability | lock edit + a sentence | CI (info) |
| adds a skill covering a new capability | lock edit + lab step, or a new unit | CI (info) + a PR |
| renames a skill | lock edit, deprecation entry | CI (error until fixed) |
| splits a skill in two | lock edit, capability may fan out | CI (error) |
| removes a skill | capability needs a new provider or the unit changes | CI (error) |
| absorbs a course tool | unit rewrites from "build it" to "wire and calibrate it" | a human |
| ships a breaking version | re-run every unit's ablation, bump the pin | warning, then judgment |

The last row is the expensive one and it should be. A breaking plugin change invalidates
the numbers in every *Our numbers* section, and stale numbers are worse than no numbers
because they look like evidence.

## 7. Why C6 exists

The course teaches skill authoring (C6 · *Authoring skills that survive*) for a reason
that isn't obvious from the curriculum: **the readers are the plugin's future
contributors.**

A reader who finishes Track C and wants `write-sensor` should be able to build it to the
plugin's standard — the description that triggers reliably, the progressive-disclosure
body, the eval that proves it helps against a no-skill baseline, and the promotion rule
that says a skill isn't stable until it's been dry-run against a real task.

That closes a loop worth closing. The course is an eval for the plugin (§3), and C6
makes it a contribution funnel too. Both artifacts get better from the same readers.

## 8. Review cadence

- **Every plugin release:** run `check_skills_map.py`, triage anything it reports.
- **Every course release:** bump `tested_against` only after re-running the affected
  units, never as a courtesy.
- **Quarterly:** re-read §5. Boundary rules drift, and the symptom is a `tools/`
  directory quietly turning into a second skill set.
