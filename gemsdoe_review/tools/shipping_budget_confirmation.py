#!/usr/bin/env python3
"""Session-5 confirmation of the spacing-4 hypothesis at the SHIPPING budget.

Why this exists
---------------
Session 4 measured, on four geographic folds with whole-system purging and a
3 px Euclidean buffer, that 88 engineered features + a genuine 4-pixel minimum
spacing beat the dense policy and matched-budget label-blind controls - but at a
REDUCED training budget (50k negatives, 100 iterations). The shipped artifact is
trained at 400k negatives / 300 iterations. A gain that only exists at the
diagnostic budget is not evidence about the file we would upload. This driver
re-runs the same experiment at the shipping budget and adds a pre-specified
layout sensitivity.

Pre-specified decision rule (written before the run; see also --print-rule)
----------------------------------------------------------------------------
  H1 (primary layout: 2x2 blocks, 4 folds, 3 px buffer, 3% budget):
      full88 budget03_spacing4 mean fold DTI  >  full88 budget03_spacing1 mean,
      AND full88 spacing4 exceeds the MAXIMUM of the three frozen null seeds
      in EVERY fold (the session-4 descriptive gate, not a significance test).
  H2 (sensitivity, two pre-specified alternative layouts):
      the SIGN of (spacing4 - spacing1) for full88 is positive on both
      (3x3 blocks/4 folds/3 px buffer) and (2x2 blocks/4 folds/5 px buffer).
  Verdict: promote the spacing-4 policy for a local candidate only if H1 and H2
  both hold. Any failure is reported as a failure. A pass is still NOT
  permission to upload: the DrivenData registration, allowance and AI disclosure
  are account-holder facts this sandbox cannot verify.

What it does NOT do: no upload, no site, no second registration, no claim of a
leaderboard score. The target is the mapped catalogue on held-out geography - a
transfer proxy, not the hidden expert labels.

    python shipping_budget_confirmation.py --entry /path/to/6GEMSDOE \\
        --scratch /scratch/session5 --configs raw19 full88 drop2
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
PRIMARY = {"blocks": 2, "folds": 4, "buffer_px": 3}
SENSITIVITY = [
    {"blocks": 3, "folds": 4, "buffer_px": 3},
    {"blocks": 2, "folds": 4, "buffer_px": 5},
]
DECISION_RULE = {
    "H1_primary": ("full88 spacing4 mean fold DTI > full88 dense(spacing1) mean AND "
                   "full88 spacing4 > max(frozen null seeds) in every fold"),
    "H2_sensitivity": "sign(full88 spacing4 - full88 spacing1) positive on both alternative layouts",
    "promotion": "only if H1 and H2 both hold; a pass is still not upload permission",
    "gate_convention": "max over three frozen null seeds is a descriptive hurdle, not a confidence interval",
}


def run(cmd: list[str], log: Path) -> None:
    with open(log, "w") as fh:
        proc = subprocess.run(cmd, stdout=fh, stderr=subprocess.STDOUT)
    if proc.returncode != 0:
        tail = "\n".join(log.read_text().splitlines()[-40:])
        raise SystemExit(f"command failed ({proc.returncode}): {' '.join(cmd)}\n{tail}")
    print("\n".join(log.read_text().splitlines()[-6:]), flush=True)


def sha256(path: Path) -> str:
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--entry", type=Path)
    ap.add_argument("--scratch", type=Path,
                    help="working directory for experiment JSON (kept out of git)")
    ap.add_argument("--configs", nargs="+", default=["raw19", "full88", "drop2"])
    ap.add_argument("--max-neg", type=int, default=400_000)
    ap.add_argument("--iters", type=int, default=300)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--skip-models", action="store_true",
                    help="geometry + controls only (fast path for a dry run)")
    ap.add_argument("--print-rule", action="store_true")
    args = ap.parse_args()
    if args.print_rule:
        print(json.dumps(DECISION_RULE, indent=2))
        return 0
    if not args.entry or not args.scratch:
        ap.error("--entry and --scratch are required unless --print-rule is given")
    entry = args.entry.resolve()
    scratch = args.scratch.resolve()
    scratch.mkdir(parents=True, exist_ok=True)
    py = sys.executable

    manifest = {
        "kind": "session-5 shipping-budget confirmation of the spacing-4 hypothesis",
        "not_a_leaderboard_score": True,
        "decision_rule": DECISION_RULE,
        "design": {"max_neg": args.max_neg, "iters": args.iters, "seed": args.seed,
                   "configs": args.configs, "primary_layout": PRIMARY,
                   "sensitivity_layouts": SENSITIVITY},
        "entry": str(entry),
        "tools": {p.name: sha256(p) for p in sorted(TOOLS.glob("*.py"))},
    }

    # ---- geometry audits: primary + both sensitivity layouts ----------------
    layouts = {"primary": PRIMARY}
    for i, lay in enumerate(SENSITIVITY):
        layouts[f"sensitivity{i + 1}"] = lay
    for tag, lay in layouts.items():
        out = scratch / f"geometry_{tag}.json"
        run([py, str(TOOLS / "spatial_system_cv.py"), "--entry", str(entry),
             "--audit-only", "--blocks", str(lay["blocks"]), "--folds", str(lay["folds"]),
             "--buffer-px", str(lay["buffer_px"]), "--out", str(out)],
            scratch / f"log_geometry_{tag}.txt")
        manifest[f"geometry_{tag}"] = {"path": out.name, "sha256": sha256(out)}

    if args.skip_models:
        manifest["complete"] = False
        manifest["note"] = "geometry-only dry run; no model scores"
        (scratch / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        return 0

    # ---- primary-layout models at the shipping budget -----------------------
    models = scratch / "models_shipping.json"
    cmd = [py, str(TOOLS / "spatial_system_cv.py"), "--entry", str(entry),
           "--blocks", str(PRIMARY["blocks"]), "--folds", str(PRIMARY["folds"]),
           "--buffer-px", str(PRIMARY["buffer_px"]),
           "--max-neg", str(args.max_neg), "--iters", str(args.iters),
           "--seed", str(args.seed), "--configs", *args.configs, "--out", str(models)]
    started = time.time()
    run(cmd, scratch / "log_models_shipping.txt")
    manifest["models_shipping"] = {"path": models.name, "sha256": sha256(models),
                                   "seconds": round(time.time() - started, 1)}

    # ---- label-blind matched-budget controls on the identical folds ---------
    controls = scratch / "controls_shipping.json"
    run([py, str(TOOLS / "spatial_controls.py"), "--entry", str(entry),
         "--geometry", str(scratch / "geometry_primary.json"), "--out", str(controls)],
        scratch / "log_controls_shipping.txt")
    manifest["controls_shipping"] = {"path": controls.name, "sha256": sha256(controls)}

    # ---- sensitivity models (full88 only, pre-specified) --------------------
    for tag in ("sensitivity1", "sensitivity2"):
        lay = layouts[tag]
        out = scratch / f"models_{tag}.json"
        run([py, str(TOOLS / "spatial_system_cv.py"), "--entry", str(entry),
             "--blocks", str(lay["blocks"]), "--folds", str(lay["folds"]),
             "--buffer-px", str(lay["buffer_px"]),
             "--max-neg", str(args.max_neg), "--iters", str(args.iters),
             "--seed", str(args.seed), "--configs", "full88", "--out", str(out)],
            scratch / f"log_models_{tag}.txt")
        manifest[f"models_{tag}"] = {"path": out.name, "sha256": sha256(out)}

    # ---- comparison (primary only; sensitivity read directly) ---------------
    comparison = scratch / "comparison_shipping.json"
    run([py, str(TOOLS / "summarize_spatial_cv.py"), "--experiment", str(models),
         "--controls", str(controls), "--out", str(comparison)],
        scratch / "log_comparison_shipping.txt")
    manifest["comparison_shipping"] = {"path": comparison.name, "sha256": sha256(comparison)}
    manifest["complete"] = True
    manifest["elapsed_seconds"] = round(time.time() - started, 1)
    (scratch / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
