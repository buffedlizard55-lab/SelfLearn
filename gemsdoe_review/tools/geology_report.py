#!/usr/bin/env python3
"""Retired rank-joined renderer: intentionally refuses to generate interpretations.

The former READINGS dictionary connected prose to integer size ranks on `ens12`.
Ranks are *not* stable across rasters, and several interpretations made unsupported
geological claims. The historic report is withdrawn; raw data remain archived.
Use `current_geology_report.py --dossier <sha256-pinned-json> --out <report.md>`
for measurements and conditional hypotheses tied to the exact submitted raster.
"""

raise SystemExit(
    "Retired unsafe rank-based renderer. Use current_geology_report.py with a "
    "SHA-256-pinned dossier; see evidence/geology_dossier.md for why."
)
