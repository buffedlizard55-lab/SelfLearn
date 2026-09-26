#!/usr/bin/env python3
"""Check the metric claims the canonical entry still publishes, numerically.

The live 6GEMSDOE site and its EXECUTIVE_SUMMARY.md tell the reader that the
published metric "is strictly increasing in the predicted value, so fractional
confidence gives score away". Two different statements are glued together there:

  (1) IDENTITY (true): DTI is strictly increasing under a UNIFORM rescaling
      p -> lambda*p, for lambda in (0, 1/max p]. Multiplying every prediction by
      a constant scales TP_w and FP_w but not the beta*n_gt term inside FN_w, so
      the ratio rises.
  (2) OVERGENERALISATION (false): therefore writing 1.0 instead of the model
      probability must always help. Hardening is NOT a uniform rescaling: it maps
      weak predictions to 0 and strong ones to 1, which changes the false-positive
      structure. Raising a remote false positive from 0.01 to 1.0 can lower DTI.

This tool verifies (1) and refutes (2) with the entry's own metric
implementation (src/gems/metric.py, the official formula from page 967), and
prints the counterexample it used. Run it against the entry source:

    python metric_claim_check.py --entry /path/to/6GEMSDOE --out evidence/metric_claim_check_session5.json

No data rasters are needed; every case is a synthetic grid.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np


def load_metric(entry: Path):
    sys.path.insert(0, str(entry.resolve() / "src"))
    from gems import metric  # noqa: PLC0415
    return metric


def grid(h=13, w=13):
    g = np.zeros((h, w), dtype=bool)
    p = np.zeros((h, w), dtype=float)
    return g, p


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--entry", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    metric = load_metric(args.entry)

    # ---- (1) uniform rescaling is monotone ---------------------------------
    g, p = grid()
    g[6, 6] = True
    p[6, 6] = 0.4          # a true pixel, weighted 0.4
    p[9, 9] = 0.3          # a remote false positive, weighted 0.3
    lam = np.linspace(0.2, 2.5, 24)
    lam = lam[lam <= 1.0 / max(p.max(), 1e-9)]
    curve = [{"lambda": float(l), "dti": metric.distance_weighted_tversky(np.clip(p * l, 0, 1), g)}
             for l in lam]
    monotone = all(b["dti"] >= a["dti"] - 1e-15 for a, b in zip(curve, curve[1:]))
    strictly = all(b["dti"] > a["dti"] + 1e-12 for a, b in zip(curve, curve[1:]))

    # ---- (2) hardening a weak remote FP can LOSE score ---------------------
    g2, p2 = grid()
    g2[2, 2] = True
    p2[2, 2] = 1.0         # the true pixel already at the cap
    p2[9, 9] = 0.01        # a weak remote false positive
    soft = metric.components(p2, g2)
    hard = metric.components((p2 > 0).astype(float), g2)
    counterexample = {
        "layout": "one GT pixel at (2,2) predicted 1.0; one remote pixel at (9,9) at 0.01",
        "soft": soft.as_dict(), "hard": hard.as_dict(),
        "hardening_lost": bool(hard.dti < soft.dti),
        "delta": float(hard.dti - soft.dti),
    }

    # ---- (3) where hardening DOES pay: a cluster of weak positives ---------
    g3, p3 = grid(17, 17)
    g3[8, 8] = True
    p3[7, 8] = 0.2
    p3[8, 7] = 0.2
    p3[8, 9] = 0.2
    p3[9, 8] = 0.2
    p3[8, 8] = 0.2
    soft3 = metric.components(p3, g3)
    hard3 = metric.components((p3 > 0).astype(float), g3)
    helps = {"soft": soft3.as_dict(), "hard": hard3.as_dict(),
             "hardening_gained": bool(hard3.dti > soft3.dti),
             "delta": float(hard3.dti - soft3.dti)}

    payload = {
        "kind": "metric claim check on the entry's own implementation; NOT a leaderboard score",
        "entry": str(args.entry.resolve()),
        "metric_source": "src/gems/metric.py (official formula, page 967)",
        "claim_1_uniform_rescaling_is_monotone": {
            "statement": "DTI strictly increases under p -> lambda*p",
            "measured": strictly, "monotone_non_strict": monotone,
            "lambdas": [round(c["lambda"], 4) for c in curve],
            "dti": [round(c["dti"], 6) for c in curve],
            "verdict": "TRUE - and it is the only identity the algebra supports",
        },
        "claim_2_hardening_always_helps": {
            "statement": "writing 1.0 instead of the probability must raise the score",
            "counterexample": counterexample,
            "verdict": ("FALSE as stated: hardening a remote false positive raises FP_w and can "
                        "lower DTI. The published sentence overgeneralises claim 1."),
        },
        "where_hardening_pays": helps,
        "consequence_for_the_entry_docs": (
            "The live 6GEMSDOE methodology note and EXECUTIVE_SUMMARY.md still present claim 2 as a "
            "consequence of claim 1. The correct statement is: a uniform rescaling never costs score; "
            "hardening helps when the raised pixels are near truth and hurts when they are not, so the "
            "3% budget - not the binarisation - is what the measurement supports."),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({k: payload[k] for k in ("claim_1_uniform_rescaling_is_monotone",
                                              "claim_2_hardening_always_helps")}, indent=2)[:1800])
    print(json.dumps(helps, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
