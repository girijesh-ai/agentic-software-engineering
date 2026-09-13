# Guides x sensors x {computational, inferential} — this repo's own harness

Audited: every mechanism in `agentic-software-engineering` that steers or checks an
agent's work, classified by the vocabulary in `docs/CURRICULUM.md` § C1. "Feedforward"
= before the agent acts (guide). "Feedback" = after, so it can self-correct (sensor).
"Computational" = deterministic, cheap. "Inferential" = semantic, model-judged, slow.

| Mechanism | Timing | Kind | Type | Notes |
|---|---|---|---|---|
| `tools/audit.sh` | Feedback | Sensor | Computational | Structural checks (line counts, sections, links, capability tags, freshness marker). Runs on every push. |
| `tools/spec_lint.py` | Feedback | Sensor | Computational | Regex/heuristic, not model-judged — deterministic despite being approximate. Its own docstring calls it heuristic on purpose. |
| `tools/check_coverage.py` | Feedback | Sensor | Computational | The CS146S superset gate. |
| `tools/check_skills_map.py` | Feedback | Sensor | Computational | Caught two real bugs this course shipped (B0's invented capability names, a plugin version drift). |
| `tools/ablation.py validate` | Feedback | Sensor | Computational | Schema/shape check on a results file — not a check on whether the *numbers* are good. |
| `.github/workflows/gates.yml` | Feedback | Sensor (aggregate) | Computational | Runs all of the above; each step independent so one red gate never hides another (a lesson from wiring it, not a stated design goal originally). |
| Every unit's `verify.sh` | Feedback | Sensor | Computational | Per-unit gate, traced to a named SC. |
| Every task's pytest verifier (`tests/ablation/test_*.py`) | Feedback | Sensor | Computational | The load-bearing one — every real ablation number in this course traces back to one of these. |
| `AGENTS.md`, `HANDOVER.md` | Feedforward | Guide | Computational | Static text, read once, never checked against. |
| Unit `README.md` § The lab | Feedforward | Guide | Computational | Same category as above. |
| `CLAUDE.md` files placed per ablation arm (B0-B3) | Feedforward | Guide | Computational | The actual object being measured in four ablations. |
| `spec-from-idea`, `plan-from-spec` (plugin skills) | Feedforward | Guide | Inferential | Model-judged proposal/pressure-testing, used by the *author* to prepare specs/plans - never invoked live by an ablated agent mid-task. |
| `grill-me` (plugin skill) | Feedforward | Guide | Inferential | Same caveat: used to prepare B1/B2's specs and plans, not available to any agent inside an ablation run. |
| `review-code` (plugin skill) | Feedback | Sensor | Inferential | Exists in the plugin. Not wired into this repo's CI or any unit's gate - see Gap 1. |
| Human grading of "wrong-problem failures" (B1 §6) | Feedback | Sensor | Inferential | Specified, never run. The one sensor this course's own thesis says only a human can provide, and it's the one still missing. |
| `mutate_and_test.py` (B3) | Feedback | Sensor | Computational | Measures whether a test suite is internally consistent with its own code - not whether either agrees with the actual spec (B3 §3.1). |
| ponytail's rung ladder (external, referenced) | Feedforward | Guide | Computational | A checklist, not model judgment - "does this need to exist" is a deterministic question to ask, even if the answer requires thought. |

## What the map does and doesn't show

Every row this repo actually built is a **computational** mechanism except the three
inferential guides (spec-from-idea, plan-from-spec, grill-me) — and every one of
those three is used by the *author preparing material*, never by an *agent being
measured*. The one inferential **sensor** this course has ever specified (human
grading of wrong-problem failures) has never run. This asymmetry is Gap 1 below, and
the map is what makes it visible rather than asserted.
