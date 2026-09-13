# C1 results

`authors-run.json` is **not a fresh ablation** - it's 120 real, unmodified run
records from `units/b1-idea-to-spec`, `units/b2-spec-to-plan`, and
`units/b3-plan-to-code`'s own `authors-run.json` files, regrouped from their
original arm labels into three guide/sensor categories (`nothing`, `guide-only`,
`guide+sensor`). Every run's `original_unit` and `original_arm` fields record where
it actually came from. See `units/c1-guides-and-sensors/README.md` §4 for why this
is the honest way to satisfy this course's "every unit survives a number" rule here,
and §6 for what the regrouping shows - including that it erases two real effects
the original, better-controlled comparisons found.

`lab-materials/` is what was actually produced:

- `coverage-map.md` - every guide/sensor mechanism in this repo's own harness,
  classified against both axes.
- `top-three-gaps.md` - three gaps, each argued from the map and from B0-B3's real
  data, not asserted from memory.
