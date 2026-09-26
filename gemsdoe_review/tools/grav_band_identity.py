#!/usr/bin/env python3
"""Session 6: what do the supplied gravity/magnetic gradient bands actually contain?

The entry (src/gems/features.py, scripts/build_features.py) and the session-5
dossier read `iso_grav_anom_hg` as the horizontal-gradient MAGNITUDE (|grad G|,
"high = density contact"). This tool tests that against numerical derivatives
of the supplied `iso_grav_anom` on the valid footprint (eroded by 2 px so the
finite differences never touch nodata):

  * signed E-W derivative dG/dx, signed N-S derivative dG/dy, |grad G|;
  * the same check for `tmi_hg` against |grad TMI| as a positive control;
  * `iso_grav_anom_slope` against |grad G|.

Spearman correlations on a fixed-seed random sample of valid pixels.

    python grav_band_identity.py --entry ../entry-src --out grav_hg_identity.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from scipy import ndimage
from scipy.stats import spearmanr

BANDS = ["iso_grav_anom", "iso_grav_anom_hg", "iso_grav_anom_vg", "iso_grav_anom_slope", "tmi", "tmi_hg"]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def identity_stats(b: dict[str, np.ndarray], invalid: np.ndarray, n_sample: int, seed: int = 0,
                   pixel_m: float = 100.0) -> dict:
    G = b["iso_grav_anom"].astype(np.float64)
    gy, gx = np.gradient(G, pixel_m)
    T = b["tmi"].astype(np.float64)
    ty, tx = np.gradient(T, pixel_m)
    inner = ndimage.binary_erosion(~invalid, iterations=2)
    for v in (gx, gy, tx, ty, b["iso_grav_anom_hg"], b["iso_grav_anom_slope"], b["tmi_hg"]):
        inner &= np.isfinite(v)
    idx = np.flatnonzero(inner.ravel())
    rs = np.random.default_rng(seed).choice(idx, size=min(n_sample, idx.size), replace=False)

    def s(a, c):
        return float(spearmanr(np.ravel(a)[rs], np.ravel(c)[rs]).statistic)

    hg = b["iso_grav_anom_hg"].astype(np.float64)
    hgm = np.hypot(gx, gy)
    return {
        "n_sample": int(rs.size),
        "hg_frac_negative": float((hg.ravel()[rs] < 0).mean()),
        "spearman_hg_vs_HGM": s(hg, hgm),
        "spearman_abs_hg_vs_HGM": s(np.abs(hg), hgm),
        "spearman_hg_vs_dGdx": s(hg, gx),
        "spearman_hg_vs_dGdy": s(hg, gy),
        "spearman_slope_vs_HGM": s(b["iso_grav_anom_slope"], hgm),
        "spearman_hg_vs_vg": s(hg, b["iso_grav_anom_vg"]),
        "tmi_check_spearman_tmi_hg_vs_HGM": s(b["tmi_hg"], np.hypot(tx, ty)),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--entry", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--n-sample", type=int, default=400_000)
    args = ap.parse_args()
    sys.path.insert(0, str(args.entry.resolve() / "src"))
    from gems import features as F  # noqa: PLC0415
    feat = args.entry / "data/training_features.tif"
    b, invalid = F.load_bands(str(feat), BANDS)
    stats = identity_stats(b, invalid, args.n_sample)
    verdict = {
        "iso_grav_anom_hg_is": ("signed E-W derivative dG/dx, NOT |grad G|"
                                if stats["spearman_hg_vs_dGdx"] > 0.9 and abs(stats["spearman_hg_vs_HGM"]) < 0.1
                                else "not established by this test"),
        "iso_grav_anom_slope_is_HGM": stats["spearman_slope_vs_HGM"] > 0.9,
        "tmi_hg_is_HGM": stats["tmi_check_spearman_tmi_hg_vs_HGM"] > 0.99,
        "consequence": ("the entry's grav_asa = sqrt(hg^2+vg^2) and grav_tilt = atan2(vg,|hg|) "
                        "(channels 25/26) ignore the N-S gradient; tmi-derived channels are unaffected"),
    }
    out = {"kind": "band identity test; label-free", "training_features_sha256": sha256(feat),
           "tool_sha256": sha256(Path(__file__)), "bands": BANDS, "stats": stats, "verdict": verdict}
    args.out.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
