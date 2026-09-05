#!/usr/bin/env python3
"""Ablation runner for harness engineering.

Runs the same task set through a coding agent twice - once with a harness, once
without - and reports whether the difference survives contact with a confidence
interval. Every module in this course is gated on producing one of these.

Standard library only, on purpose. A measurement tool that needs its own
dependency resolution is a measurement tool nobody runs.

    python tools/ablation.py run     config.json -o results/authors-run.json
    python tools/ablation.py report  results/authors-run.json
    python tools/ablation.py validate results/baseline.json

Config shape (JSON):

    {
      "module_id": "m00",
      "agent_command": "claude -p \\"$(cat {prompt_file})\\" --permission-mode acceptEdits",
      "repeats": 3,
      "timeout_sec": 900,
      "workdir": ".",
      "arms": [
        {"name": "no-harness", "setup": "git checkout ablation/bare -- AGENTS.md docs/"},
        {"name": "harness",    "setup": "git checkout main -- AGENTS.md docs/"}
      ],
      "tasks": [
        {
          "id": "add-feature-column",
          "prompt": "Add a rolling 7-day mean of `amount` to the feature builder.",
          "reset": "git checkout . && git clean -fd",
          "verifier": "pytest tests/test_features.py -q"
        }
      ]
    }

The verifier is the load-bearing field. If you cannot write one for a task, that
task does not belong in an ablation - you would be measuring your own opinion.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import statistics
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = 1


# --------------------------------------------------------------------------- #
# running
# --------------------------------------------------------------------------- #

def _shell(cmd: str, cwd: str, timeout: int) -> tuple[int, float, str]:
    """Run a shell command. Returns (returncode, wall_seconds, tail_of_output)."""
    started = time.monotonic()
    try:
        proc = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            timeout=timeout,
            capture_output=True,
            text=True,
        )
        rc, out = proc.returncode, (proc.stdout + proc.stderr)
    except subprocess.TimeoutExpired:
        rc, out = 124, f"TIMEOUT after {timeout}s"
    except Exception as exc:  # noqa: BLE001 - a broken command is data, not a crash
        rc, out = 125, f"RUNNER ERROR: {exc}"
    return rc, time.monotonic() - started, out[-4000:]


def run_ablation(config: dict, dry_run: bool = False) -> dict:
    workdir = config.get("workdir", ".")
    repeats = int(config.get("repeats", 3))
    timeout = int(config.get("timeout_sec", 900))
    agent_command = config["agent_command"]

    runs: list[dict] = []
    total = len(config["arms"]) * len(config["tasks"]) * repeats
    done = 0

    for arm in config["arms"]:
        for task in config["tasks"]:
            for rep in range(repeats):
                done += 1
                label = f"[{done}/{total}] {arm['name']} / {task['id']} / rep{rep}"
                print(label, file=sys.stderr, flush=True)

                if dry_run:
                    runs.append(_fake_run(arm, task, rep))
                    continue

                # Reset the working tree, then configure the arm's harness.
                if task.get("reset"):
                    _shell(task["reset"], workdir, 120)
                if arm.get("setup"):
                    _shell(arm["setup"], workdir, 120)

                with tempfile.NamedTemporaryFile(
                    "w", suffix=".txt", delete=False, encoding="utf-8"
                ) as fh:
                    fh.write(task["prompt"])
                    prompt_file = fh.name
                try:
                    cmd = agent_command.format(prompt_file=prompt_file)
                    agent_rc, agent_wall, agent_out = _shell(cmd, workdir, timeout)
                finally:
                    os.unlink(prompt_file)

                ver_rc, ver_wall, ver_out = _shell(task["verifier"], workdir, timeout)

                runs.append(
                    {
                        "arm": arm["name"],
                        "task": task["id"],
                        "repeat": rep,
                        "passed": ver_rc == 0,
                        "agent_returncode": agent_rc,
                        "agent_wall_sec": round(agent_wall, 2),
                        "verifier_wall_sec": round(ver_wall, 2),
                        "agent_tail": agent_out[-1500:],
                        "verifier_tail": ver_out[-1500:],
                    }
                )

    return {
        "schema_version": SCHEMA_VERSION,
        "module_id": config.get("module_id", "unknown"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dry_run": dry_run,
        "config": {
            "repeats": repeats,
            "timeout_sec": timeout,
            "agent_command": agent_command,
            "arms": [a["name"] for a in config["arms"]],
            "tasks": [t["id"] for t in config["tasks"]],
            "verifiers": {t["id"]: t["verifier"] for t in config["tasks"]},
        },
        "runs": runs,
        "summary": summarize(runs),
    }


def _fake_run(arm: dict, task: dict, rep: int) -> dict:
    """Synthetic run so the pipeline can be exercised without burning tokens."""
    rng = random.Random(f"{arm['name']}/{task['id']}/{rep}")
    harnessed = arm["name"] != "no-harness"
    passed = rng.random() < (0.72 if harnessed else 0.38)
    return {
        "arm": arm["name"],
        "task": task["id"],
        "repeat": rep,
        "passed": passed,
        "agent_returncode": 0,
        "agent_wall_sec": round(rng.uniform(60, 400), 2),
        "verifier_wall_sec": round(rng.uniform(1, 30), 2),
        "agent_tail": "(dry run)",
        "verifier_tail": "(dry run)",
    }


# --------------------------------------------------------------------------- #
# statistics
# --------------------------------------------------------------------------- #

def _bootstrap_ci(
    a: list[float], b: list[float], iters: int = 10000, seed: int = 7
) -> tuple[float, float]:
    """Percentile bootstrap CI for mean(b) - mean(a). Non-parametric on purpose:
    pass/fail counts at K=3 are nowhere near normal."""
    if not a or not b:
        return (float("nan"), float("nan"))
    rng = random.Random(seed)
    diffs = []
    for _ in range(iters):
        ra = [a[rng.randrange(len(a))] for _ in a]
        rb = [b[rng.randrange(len(b))] for _ in b]
        diffs.append(statistics.fmean(rb) - statistics.fmean(ra))
    diffs.sort()
    lo = diffs[int(0.025 * len(diffs))]
    hi = diffs[int(0.975 * len(diffs)) - 1]
    return (round(lo, 4), round(hi, 4))


def summarize(runs: list[dict]) -> dict:
    # First-seen order, not alphabetical: the config lists the baseline arm first,
    # and sorting would silently invert the sign of every reported delta.
    arms: list[str] = []
    for r in runs:
        if r["arm"] not in arms:
            arms.append(r["arm"])
    per_arm: dict[str, dict] = {}

    for arm in arms:
        rows = [r for r in runs if r["arm"] == arm]
        walls = [r["agent_wall_sec"] for r in rows]
        per_arm[arm] = {
            "n": len(rows),
            "pass_rate": round(statistics.fmean(1.0 if r["passed"] else 0.0 for r in rows), 4),
            "median_agent_wall_sec": round(statistics.median(walls), 1) if walls else None,
            "per_task_pass_rate": {
                t: round(
                    statistics.fmean(
                        1.0 if r["passed"] else 0.0
                        for r in rows
                        if r["task"] == t
                    ),
                    4,
                )
                for t in sorted({r["task"] for r in rows})
            },
        }

    comparison = None
    if len(arms) == 2:
        base, treat = arms[0], arms[1]
        a = [1.0 if r["passed"] else 0.0 for r in runs if r["arm"] == base]
        b = [1.0 if r["passed"] else 0.0 for r in runs if r["arm"] == treat]
        lo, hi = _bootstrap_ci(a, b)
        comparison = {
            "baseline_arm": base,
            "treatment_arm": treat,
            "pass_rate_delta": round(statistics.fmean(b) - statistics.fmean(a), 4),
            "ci95": [lo, hi],
            "crosses_zero": bool(lo <= 0 <= hi),
        }

    return {"per_arm": per_arm, "comparison": comparison}


# --------------------------------------------------------------------------- #
# reporting and validation
# --------------------------------------------------------------------------- #

def render_report(result: dict) -> str:
    s = result["summary"]
    lines = [
        f"# Ablation — {result['module_id']}",
        "",
        f"Generated {result['generated_at']}"
        + ("  ·  **DRY RUN, not real data**" if result.get("dry_run") else ""),
        "",
        "| Arm | n | Pass rate | Median agent wall (s) |",
        "|---|---|---|---|",
    ]
    for arm, st in s["per_arm"].items():
        lines.append(
            f"| {arm} | {st['n']} | {st['pass_rate']:.0%} | {st['median_agent_wall_sec']} |"
        )

    c = s.get("comparison")
    if c:
        verdict = (
            "**Inconclusive** — the interval crosses zero. More repeats, or the "
            "effect is not there."
            if c["crosses_zero"]
            else "**Effect detected** — the interval excludes zero."
        )
        lines += [
            "",
            f"`{c['treatment_arm']}` vs `{c['baseline_arm']}`: "
            f"**{c['pass_rate_delta']:+.1%}** pass rate "
            f"(95% CI {c['ci95'][0]:+.3f} to {c['ci95'][1]:+.3f})",
            "",
            verdict,
        ]

    lines += ["", "## Per task", "", "| Task | " + " | ".join(s["per_arm"]) + " |",
              "|---|" + "---|" * len(s["per_arm"])]
    tasks = sorted(next(iter(s["per_arm"].values()))["per_task_pass_rate"])
    for t in tasks:
        cells = [f"{s['per_arm'][a]['per_task_pass_rate'].get(t, 0):.0%}" for a in s["per_arm"]]
        lines.append(f"| {t} | " + " | ".join(cells) + " |")

    lines += [
        "",
        "> Report null and negative results. A module whose harness did nothing is a",
        "> finding, and publishing it is why anyone should believe the modules where",
        "> the harness did something.",
    ]
    return "\n".join(lines)


def validate(result: dict) -> list[str]:
    """SC-1 / SC-2 conformance. Returns a list of problems; empty means valid."""
    problems: list[str] = []

    if result.get("schema_version") != SCHEMA_VERSION:
        problems.append(f"schema_version must be {SCHEMA_VERSION}")
    if result.get("dry_run"):
        problems.append("dry_run results are not admissible as a module result")

    cfg = result.get("config", {})
    runs = result.get("runs", [])
    arms = {r["arm"] for r in runs}
    tasks = {r["task"] for r in runs}

    if len(arms) < 2:
        problems.append(f"need >=2 arms (with and without harness), found {len(arms)}")
    if len(tasks) < 5:
        problems.append(f"need >=5 tasks, found {len(tasks)}")
    if int(cfg.get("repeats", 0)) < 3:
        problems.append(f"need >=3 repeats, found {cfg.get('repeats')}")

    for t in tasks:
        v = cfg.get("verifiers", {}).get(t)
        if not v:
            problems.append(f"task '{t}' has no recorded verifier command")

    for arm in arms:
        for t in tasks:
            n = sum(1 for r in runs if r["arm"] == arm and r["task"] == t)
            if n < int(cfg.get("repeats", 3)):
                problems.append(f"arm '{arm}' task '{t}' has {n} runs, expected >= repeats")

    return problems


# --------------------------------------------------------------------------- #

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("run", help="run an ablation from a config file")
    r.add_argument("config")
    r.add_argument("-o", "--out", default="results/ablation.json")
    r.add_argument("--dry-run", action="store_true",
                   help="synthesise runs to exercise the pipeline without spending tokens")

    rep = sub.add_parser("report", help="render a markdown report")
    rep.add_argument("result")

    val = sub.add_parser("validate", help="check a result against the course contract")
    val.add_argument("result")

    args = p.parse_args()

    if args.cmd == "run":
        config = json.loads(Path(args.config).read_text(encoding="utf-8"))
        result = run_ablation(config, dry_run=args.dry_run)
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"\nwrote {out}\n", file=sys.stderr)
        print(render_report(result))
        return 0

    if args.cmd == "report":
        print(render_report(json.loads(Path(args.result).read_text(encoding="utf-8"))))
        return 0

    problems = validate(json.loads(Path(args.result).read_text(encoding="utf-8")))
    if problems:
        print("INVALID:", file=sys.stderr)
        for prob in problems:
            print(f"  - {prob}", file=sys.stderr)
        return 1
    print("valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
