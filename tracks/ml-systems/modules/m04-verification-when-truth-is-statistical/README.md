# M04 · Verification when truth is statistical

> Reference module. This is the shape and depth every other module must hit.

**Prerequisites.** M00 (you have a baseline), M01 (you have a coverage map).
**Time.** ~3 hours. **Cost.** Under $5 in agent tokens; no GPU required.
**Serves.** SC-3.

---

## 1. The question

AUC moved from 0.834 to 0.831. Is that a regression?

## 2. The failure

Run this on your own repo before reading further. Give your agent a task like
*"speed up the feature pipeline; don't hurt model quality"* and let it work
unsupervised for twenty minutes.

Then look at what it did with the metric. In our runs, four distinct failures showed
up, and they are all the same failure wearing different clothes:

| What the agent did | Why the harness let it |
|---|---|
| Reported "AUC 0.831, essentially unchanged" and moved on | No sensor. The float was for a human, and no human was there. |
| Changed the eval split to one where the number looked better | The sensor read a metric but nothing pinned the thing producing it. |
| Chased a 0.003 drop for eleven turns; it was seed noise | Threshold set by vibes, tighter than the noise floor. |
| Passed a 4-point real regression | Threshold set by vibes, looser than the effect. |

Every published harness assumes verification is boolean, fast, cheap and
deterministic. Anthropic says this directly about their own long-running-agent
work — the demo is optimised for full-stack web development, and generalising to
other fields is named as future work. This module is that generalisation for the
field where the assumption breaks hardest.

The core problem: **an agent cannot act on a float.** It needs a boolean. And a
badly calibrated boolean is worse than no sensor at all, because the agent trusts it.

## 3. The idea

### 3.1 Measure the noise floor before you pick a threshold

Almost everyone picks a tolerance by feel — 1%, or 0.005, or "half a point." Then
they spend weeks confused about why CI is flaky, or why regressions slip through.

The threshold is not a preference. It is an empirical property of your pipeline, and
you measure it the same way you'd measure any other property:

```
run the unchanged pipeline K times with K different seeds
record the metric each time
your noise floor is the spread of that distribution
your threshold sits outside it, with a stated confidence level
```

K=20 is usually enough and usually cheap on a subset. Write the number down in the
repo — it is a fact about your system, it belongs next to the code, and it will drift
as your data does. Re-measure it quarterly, or make a sensor that does.

The output is not one number but three, and they do different jobs:

- **Noise band** — the range within which a change is indistinguishable from a
  re-run. Nothing inside it is signal. A verifier that fires here is broken.
- **Gate threshold** — outside the noise band, with margin. Crossing it fails the build.
- **Watch threshold** — between the two. Doesn't fail; gets recorded and reported.
  This is where slow degradation lives, and a binary gate is blind to it.

### 3.2 Separate contract violations from metric movement

These get conflated constantly and they need completely different sensors.

A **contract violation** is boolean, deterministic, and cheap: output schema changed,
a column went null, prediction count doesn't match input count, a probability escaped
[0,1], inference latency blew its budget, the model file didn't get written. This is
just software. Test it like software — fast, hard gate, on every change.

A **metric movement** is statistical, expensive and noisy. Only this needs the noise
floor machinery.

Most "the agent broke the model" incidents are contract violations wearing a metric
costume. Build the contract tier first. It is 90% of the value at 2% of the cost, and
you can run it on a fixture in under a second.

### 3.3 Pin everything you can, then record what you couldn't

Set seeds for Python's `random`, NumPy, and your framework; set `PYTHONHASHSEED`;
force deterministic kernels where the framework offers them; pin the data version.

Then accept that some non-determinism survives — GPU reductions, thread scheduling,
parallel data loading order, some library internals. Don't pretend otherwise. Record
the environment fingerprint alongside every result, so that when a number moves you
can tell whether the *code* moved or the *floor* did.

The failure this prevents is subtle and expensive: an agent that "fixes" a regression
that was actually caused by a CUDA version bump, and in doing so damages the model to
chase a ghost.

### 3.4 Write the failure message for the agent, not for you

This is the highest-leverage paragraph in this module.

OpenAI's team writes custom lints specifically so they can **inject remediation
instructions into agent context through the error message**. Böckeler calls the same
technique a positive kind of prompt injection: a sensor whose output is optimised for
LLM consumption rather than human reading.

Compare. Here is the sensor most people write:

```
FAIL: auc=0.8285 threshold=0.8300
```

The agent now has a number and no idea what to do, so it guesses. Usually it lowers
the threshold, because that is the fastest path to green and nothing told it not to.

Here is the same sensor written for its actual reader:

```
FAIL: eval/auc regression on the `churn_30d` model.

  observed   0.8285   (seeds 11,12,13 | median of 3)
  baseline   0.8341   (results/baseline.json, recorded 2026-08-02)
  delta     -0.0056
  noise band ±0.0021  (measured over 20 seeds, docs/noise-floor.md)

  The delta is 2.7x the noise band. This is a real regression, not seed variance.

  Do NOT change the threshold, the seeds, or the eval split. Those are pinned
  in eval/config.yaml and changing them will fail the pinning check.

  Likely causes, in the order worth checking:
    1. Feature drop or dtype change in features/build.py  -> `git diff features/`
    2. Train/eval split leakage  -> `make check-leakage`
    3. Preprocessing order changed -> compare pipeline steps against
       docs/pipeline-contract.md

  To reproduce locally: `make eval-subset MODEL=churn_30d SEEDS=11,12,13`  (~4 min)
```

Same check. Roughly forty extra lines of Python, written once. In our runs this
single change was worth more than every other guide in the module combined — the
agent stopped guessing and started following the trail, and stopped reaching for the
threshold as the first fix.

Two rules that make this work:

1. **Name the things it must not touch.** Agents optimise for green. If you don't say
   the threshold is off-limits, you have implicitly offered it as a solution.
2. **Back the prohibition with a sensor.** A pinning check that fails if
   `eval/config.yaml` changed in the same commit as an eval fix. Instructions are a
   guide; the guide needs a sensor or the agent will eventually route around it.

### 3.5 Report the trend, not just the verdict

A gate is memoryless. Six changes that each move the metric 0.0015 — every one inside
the noise band, every one passing — is a 0.009 regression that no gate ever saw.

Cheap fix: append every gate run to `results/metric-history.jsonl` and add a second,
slower sensor that runs weekly, fits a trend over the last N results, and fails if the
slope is negative beyond a threshold. This is a continuous drift sensor rather than a
change-lifecycle sensor, and ML systems need it more than most software because they
also degrade on their own, without anybody touching them.

## 4. The lab

You will build a calibrated verifier for one real ML task in your own repo.

**Step 1 — Contract tier (30 min).**
Write `verify_contract.py`: schema, row counts, null rates, value ranges, artifact
existence. Runs on a micro-fixture. Must complete in under one second. Hard gate.

**Step 2 — Measure your noise floor (45 min).**
Run your eval unchanged 20 times on a subset with 20 seeds. Record the distribution.
Write `docs/noise-floor.md` with the measurement, the date, the environment
fingerprint, and the three thresholds derived from it. Commit it.

**Step 3 — Build the calibrated verifier (45 min).**
`verify_metric.py`: median of 3 seeds against a recorded baseline, compared to your
measured band. Emits pass, watch or fail. Failure message follows §3.4 — named
prohibitions, ranked causes, a reproduce command.

**Step 4 — Add the pinning sensor (15 min).**
Fails if seeds, thresholds or the eval split changed in the same commit as a fix.

**Step 5 — Test the verifier against three seeded scenarios (30 min).**
Provided in `fixtures/`:
- `true-pass` — a real improvement. Must pass.
- `true-regression` — a real 4-point drop. Must fail.
- `noise-wobble` — a within-band re-run. **Must pass.**

The third one is the whole point. A verifier that fires on the wobble is
mis-calibrated, and mis-calibrated is not "cautious" — it is the thing that teaches an
agent to chase ghosts and burn your GPU budget doing it.

**Step 6 — Measure it (15 min).**
Re-run the M00 task from §2 with the verifier in place. Record in
`results/learner-run.json`.

## 5. The gate

```bash
./verify.sh
```

Passes when: contract tier under 1s; noise floor documented with K≥20; the verifier
gets all three fixtures right; the pinning sensor fires on a tampered config; and
`results/learner-run.json` validates.

Traced to **SC-3**.

## 6. Our numbers

> Placeholder — this section must be filled with a real
> `results/authors-run.json` before this module ships. Per SC-2, CI fails the build
> without it, and per house style it reports null and negative results too. Do not
> publish this module with invented numbers; the credibility of the whole course
> rests on this section being honest.

Planned reporting shape:

| Arm | Pass rate | Median turns | Median wall | Cost/task |
|---|---|---|---|---|
| No verifier | — | — | — | — |
| Uncalibrated verifier (guessed threshold) | — | — | — | — |
| Calibrated verifier, plain failure message | — | — | — | — |
| Calibrated verifier, agent-directed message (§3.4) | — | — | — | — |

The three-way split between the middle rows is the interesting comparison and the one
we most expect to surprise us. Our hypothesis is that the uncalibrated verifier scores
*worse than no verifier* on wall time and cost — a false gate is an active tax. If the
data says otherwise, the data wins and this module gets rewritten.

## 7. What makes this obsolete

Faster than most of the course. Watch for:

- **Models that reason well about statistical significance unaided.** If an agent can
  read a raw metric history and correctly conclude "that's within noise," the
  calibration machinery collapses into just recording the history. The failure message
  work survives; the threshold work mostly doesn't.
- **Harness-native metric tracking.** If agent runtimes start carrying first-class
  metric-baseline primitives, this becomes configuration rather than construction.
- **Cheap enough verification.** If a full eval run costs cents and takes seconds, the
  tiering in M05 stops mattering and you just run everything.

What does **not** go obsolete: deciding what "good" means and writing it down. That is
the behaviour harness (M03), and it gets more load-bearing as models improve, not less.

## 8. Sources

- OpenAI — *Harness engineering: leveraging Codex in an agent-first world* (custom
  lints carrying remediation instructions; enforcing invariants over implementations)
- Anthropic — *Effective harnesses for long-running agents* (self-verification;
  the premature-completion failure mode; the explicit scope limit to web development)
- Anthropic — *Demystifying evals for AI agents*
- Böckeler / Thoughtworks — *Harness engineering for coding agent users*
  (guides/sensors; computational vs inferential; sensors optimised for LLM consumption)
- LangChain — *Improving Deep Agents with harness engineering* (build-verify loops;
  harness-only gains at fixed model)
- SandMLE (Meta AI) — micro-scale sandboxes for fast MLE verification
- MLE-Dojo — iterative MLE environments with real-time outcome verification
