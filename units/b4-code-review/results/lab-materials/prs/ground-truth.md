# Ground truth for the 5 PRs

Each PR is a real diff (`pr{1..5}.diff`) against B2/B3's reference implementation
(`units/b3-plan-to-code/results/lab-materials/reference-implementation/`), constructed
to cover the review-code cases that matter: a clear spec violation, a subtle one, a
clean PR, and two standards/security issues independent of the spec. Ground truth is
recorded here, not visible to the reviewers.

| PR | One-line ticket | Real defect | Type | Should a correct review say READY or NEEDS FIXES? |
|---|---|---|---|---|
| 1 | "Let viewers toggle an item's read status" | `update_item` was changed to accept `ViewableItem` instead of `EditableItem` - now a viewer can update the entire item (title, description), not just a "read" flag that doesn't even exist in the model. | Spec violation - direct: SC-2 says a viewer must get 403 on write. | NEEDS FIXES |
| 2 | "Let any team member see the team roster" | Correctly scoped to current members only (403 for non-members, matching how item access works), reuses existing session/model patterns. No defect. | Clean | READY |
| 3 | "Let team owners rename their team" | Correctly restricts to owners (spec-adjacent, satisfies the implicit "owner manages the team" expectation) but duplicates the owner check inline instead of calling the existing `_require_owner` helper already defined two functions above, and adds an out-of-place import line instead of grouping it with the existing `sqlmodel` import. | Standards violation (DRY / import hygiene), spec-compliant | NEEDS FIXES (Axis 2 only - Axis 1 has nothing to flag, since no SC covers renaming) |
| 4 | "Let editors bulk-delete a team's items" | Grants `Role.editor` bulk-delete access. SC-3/SC-4 state delete is owner-only for individual items; this new endpoint deletes many items at once at the *editor* threshold. The code is otherwise well-formed, authenticated, and cites a plausible (but wrong) precedent in its own docstring. | Spec violation - subtle: requires cross-referencing the specific role threshold against SC-3/SC-4, not just checking "is there an auth check." | NEEDS FIXES |
| 5 | "Let users view a team's details by ID" | The new `read_team` endpoint takes no `CurrentUser` dependency at all - it is reachable with no authentication, and returns team info to anyone including non-members. | Standards/security violation, unrelated to any stated SC (the spec never addresses team-detail visibility) | NEEDS FIXES (Axis 2 only - Axis 1 has nothing to flag, since no SC covers this endpoint) |

**Design intent:** PR1 and PR4 test whether the spec axis catches violations of an
explicit written criterion (PR1: obviously so; PR4: only by checking the *specific*
role threshold, not just "is it authenticated"). PR2 is the null case - a reviewer
that flags issues on clean code is worse than one that finds nothing. PR3 and PR5
test whether Axis 2 (standards) fires regardless of spec availability, since neither
issue is spec-related - the spec-withheld condition should catch these exactly as
well as the spec-provided condition.
