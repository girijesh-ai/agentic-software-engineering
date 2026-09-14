# C3 · Enforcing architecture and taste

**Prerequisites.** B2 (the architecture decision this unit's linter enforces),
B3 (the reference implementation this unit's lab runs against).
**Time.** ~2.5 hours. **Cost.** Under $5 in agent tokens.

<!-- capabilities: architecture-lens, code-standards, sensor-authoring, overbuild-audit -->
**Serves.** SC-4, SC-5.

---

## 1. The question

How do you make a rule that the agent can't route around?

## 2. The failure

B2's plan made one real architecture decision: item permission is decided in
exactly one place, `app/api/deps.py`'s `get_item_with_permission` dependency, not
repeated inline per handler. B3 built it. Nothing in this repo stops that decision
from silently eroding — a future handler, written under time pressure or by an
agent that never read B2's plan, can trivially reintroduce the pre-refactor
pattern (`if not current_user.is_superuser and item.owner_id != current_user.id`)
and nothing catches it. "Follow the architecture" is a sentence in a markdown
file nobody re-reads.

This unit's own lab produced a sharper failure than the one it set out to
demonstrate. The plan was: write a linter, ablate a bare-verdict message against
a remediation-carrying one, expect the better message to fix things faster or
more often. The real data (§6) shows something more specific and more useful:
**27 of 28 real failures across both message styles failed for the identical
reason** — the agent correctly removed the inline check (satisfying the linter)
but picked the wrong replacement, `OwnedItem` instead of `EditableItem`, because
neither message style tells it which of the three role levels is correct. That's
not a message-quality problem. It's a boundary this class of sensor cannot cross
by writing a better error message, which is a more useful finding for the unit's
own thesis than the comparison it was built to run.

## 3. The idea

### 3.1 Enforce invariants, not implementations

The linter (`check_permission_pattern.py`) doesn't check *what* a handler does —
it checks that single-item routes (`GET`/`PUT`/`DELETE /items/{id}`) never
reference `owner_id` or `is_superuser` directly in their own body. List, count,
and create routes are explicitly exempt (§3.2), because they legitimately need
that logic themselves — the invariant is scoped to what the architecture decision
actually claimed, not to every occurrence of those two names in the file. An
earlier version of this linter flagged all three exempt routes as violations; the
first thing it caught was its own over-broad scope, fixed before any real ablation
ran (see `results/lab-materials/check_permission_pattern.py`'s
`_is_single_item_route` and the comment explaining why).

### 3.2 The remediation-message trick, and its real ceiling

C3's headline trick — write failure output carrying what's wrong, what must not
be touched, ranked likely causes, and a reproduce command — is built exactly as
specified (`check_permission_pattern.py --remediate`). §6's data is the honest
report on what it actually bought here: nothing measurable, because the specific
piece of information an agent needed (*which* of `ViewableItem`/`EditableItem`/
`OwnedItem` is correct for this particular handler) is domain knowledge the
linter itself doesn't have. It's a syntactic, AST-level check — it knows a
handler references a flagged name, not what permission level that handler is
supposed to enforce. A remediation message can carry everything the sensor
actually knows. It cannot carry what the sensor was never told. This is
harnessability in reverse: the sensor is cheap and reliable exactly because it's
scoped to a mechanically checkable pattern, and that same scoping is why its
remediation has a hard ceiling.

### 3.3 What the passing runs actually did

The three runs (of 30) that picked the correct role didn't get better
instructions — both arms' prompts and messages were identical on this point.
Reading their closing summaries (§6), each one explicitly reasoned by analogy
from the *other* two handlers still visible in the same file: "`read_item()` uses
`ViewableItem`, `delete_item()` uses `OwnedItem`, so `update_item()` should use
`EditableItem`." The information that resolved the ambiguity was already in the
codebase, sitting next to the violation, and neither message pointed at it. That
is a concrete, implementable improvement neither arm tested — see §7.

## 4. The lab

**Step 1 — Write the linter (done for this unit).**
[`check_permission_pattern.py`](results/lab-materials/check_permission_pattern.py):
AST-based, standard library only, scoped to single-item routes only (§3.1). Two
modes: bare verdict, and `--remediate` (what's wrong, what must not be touched,
ranked likely causes, reproduce command).

**Step 2 — Seed a real violation (done for this unit).**
[`seed_violation.py`](results/lab-materials/seed_violation.py) reintroduces the
exact pre-refactor inline check into `update_item()`. Confirmed the linter fires
on it and stays silent on the clean reference implementation before trusting
either message mode.

**Step 3 — Ablate message style on a real regression.** Baseline: B2/B3's
reference implementation, committed as a clean starting point (not the bare
upstream template — this lab is specifically about a codebase that already has
the architecture decision in place and needs it defended, not built). Both arms
get the identical seeded violation; only the linter's own output style differs
(`LINT_OUTPUT.md`, written by the arm's setup step, either bare or
`--remediate`). Verifier: the linter itself must pass, and B2's 9-test permission
suite must still pass — a fix that satisfies the linter but breaks the actual
permission semantics (§6) does not count as a pass.

## 5. The gate

```bash
./verify.sh
```

Passes when: `check_permission_pattern.py` exists and is non-empty;
`results/authors-run.json` is a real (non-dry-run) run with exactly the `bare`
and `remediation` arms, each with at least 3 repeats. Does **not** call
`tools/ablation.py validate` directly — that check requires ≥5 distinct tasks, a
shape built for B0-C1's multi-ticket ablations. This unit's real shape is one
linter and one seeded violation, ablated on message style, exactly as
`docs/CURRICULUM.md`'s own C3 lab describes it ("the same linter emitting a bare
verdict"). Inventing four more unrelated task IDs to satisfy a schema built for a
different lab shape would be manufacturing task diversity, not measuring
anything real — `verify.sh` checks the invariants that actually apply here
instead, and says why in its own header comment.

Traced to **SC-4** (a sensor whose failure output carries all four remediation
elements) and **SC-5** (an ablation comparing it against a bare verdict) in
[`docs/COURSE-SPEC.md`](../../docs/COURSE-SPEC.md).

## 6. Our numbers

Real run: `results/authors-run.json`, 30 invocations (2 arms × 1 task × 15
repeats), `claude-haiku-4-5`, against the B2/B3 reference implementation with a
seeded violation reset between every run. Verified 2026-09-14.

| Arm | Pass rate | Median agent wall (s) |
|---|---|---|
| Bare verdict | 13% (2/15) | 47.8 |
| Remediation-carrying | 7% (1/15) | 35.8 |

`remediation` vs `bare`: **-6.7pp** (95% CI -0.267 to +0.133 — inconclusive,
interval crosses zero). At face value this looks like a null result on the
question the ablation was designed to answer. It's more specific than that.

**All 28 failures were the same failure.** Every single failing run — 13 of 15
bare, 14 of 15 remediation — failed `test_editor_read_write_no_delete` and only
that test. The agent correctly diagnosed the lint violation, correctly removed
the inline check, correctly picked *a* dependency from
`ViewableItem`/`EditableItem`/`OwnedItem`, and picked `OwnedItem` instead of the
correct `EditableItem` in every one of the 27 wrong cases. Not one run left the
inline check in place, invented a fourth approach, or broke anything else. This
is 27 near-identical, well-formed, plausible fixes to the wrong specific
question — B1's opening thesis, recurring inside this unit's own ablation.

**Why message style didn't move this.** Neither the bare verdict nor the
remediation message states which role level is correct — because
`check_permission_pattern.py` is a syntactic AST check with no notion of what
"editor" means for this endpoint; it can name the pattern (a flagged identifier
in a single-item handler) but not the semantics (which of three roles this
specific handler should require). The remediation message's four elements
(what's wrong, what not to touch, ranked causes, reproduce command) are exactly
what the sensor legitimately knows. The missing fact was never in either
message, so improving the message's *presentation* had nothing to work with —
consistent with §3.2's harnessability argument, not a contradiction of it.

**What the 3 passing runs did instead.** Read directly (§3.3): all three
reasoned from the two other single-item handlers already visible in the same
file, correctly inferring `update_item` was the missing third role by analogy.
That information was sitting in the codebase the whole time, available to every
run in both arms, and neither message pointed at it. This is the concrete,
testable next step this unit's own data suggests — not "write a better verdict
sentence," but "point the sensor at context it isn't currently using."

## 7. What makes this obsolete

If a linter can be handed enough of the surrounding codebase's own already-correct
usages to infer the missing semantic fact itself — effectively becoming an
inferential check that reasons from precedent, not a purely syntactic one — the
specific gap this unit's data found would close, and the interesting question
would move to whether *that* sensor's remediation message matters. Vercel's
`react-best-practices` (`docs/ECOSYSTEM-MAP.md`) already gestures at this with
ordered rules; a sensor that cites the three sibling handlers by name in its
remediation message, rather than just naming the three possible dependencies, is
a small, concrete extension worth trying before this unit's numbers are trusted
as final. Separately: `skills.lock.json`'s `sensor-authoring` expected-gap entry
would obsolete the hand-rolled linter lab specifically, once the plugin ships an
equivalent skill.

## 8. Sources

- `docs/CURRICULUM.md` § C3 — the guide-that-can't-be-routed-around framing, the
  remediation-message trick, and the lab this unit's ablation follows directly.
- `docs/COURSE-SPEC.md` SC-4, SC-5 — the four-element remediation requirement and
  the message-style ablation this unit's gate traces to.
- `units/b2-spec-to-plan/results/lab-materials/plan-team-sharing.md` §
  "Architecture decision" — the exact invariant this unit's linter enforces.
- `units/c1-guides-and-sensors/results/lab-materials/coverage-map.md` — the
  computational-sensor row this unit adds a second, sharper instance of.
