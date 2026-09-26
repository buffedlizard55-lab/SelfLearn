#!/usr/bin/env python3
"""scripts/prepare_data.py — inspect placed competition rasters against the official spec.

Pure standard library: this repository ships with no third-party dependencies, so the
GeoTIFF header is parsed by hand (classic TIFF; BigTIFF is reported, not parsed).
The official spec checked here is quoted from the problem description and submission
format sections of https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
(fetched and archived 2026-09-26; see docs/research/):

  training_features.tif — "a projected coordinate system for UTM zone 11N (EPSG 32611)
                           at 100m resolution", many layers, one feature per band.
  submission template   — same CRS, same 100 m resolution, same bounds as the training
                           data, data outside the bounds null/NaN, a single layer,
                           float32, values between 0 and 1.
  existing_faults.tif   — training labels at 100 m resolution; positively labelled
                           pixels indicate fault presence (rules §3.3).

This script inspects and reports only. It never generates, edits, or validates a
prediction GeoTIFF; submission generation is a separate, explicitly gated process.

Exit codes: 0 all expected files present and conforming · 2 nothing placed
            3 files placed but one or more spec checks failed (details in JSON).
"""

from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = DATA / "inventory.json"

EXPECTED = {
    "training_features.tif": {"crs_epsg": 32611, "res_m": 100.0},
    "existing_faults.tif": {"crs_epsg": 32611, "res_m": 100.0},
    "example_submission.tif": {"crs_epsg": 32611, "res_m": 100.0, "float32_single_band": True},
}

TYPE_SIZE = {1: 1, 2: 1, 3: 2, 4: 4, 5: 8, 6: 1, 7: 1, 8: 2, 9: 4, 10: 8, 11: 4, 12: 8}

# GeoTIFF tag numbers (EPSG: 3.3.1 of GeoTIFF 1.1; GDAL follows it)
T_IMAGEWIDTH, T_IMAGELENGTH, T_BITSPERSAMPLE = 256, 257, 258
T_SAMPLEFORMAT, T_MODELPIXELSCALE, T_MODELTIEPOINT = 339, 33550, 33922
T_GEOKEYDIR, T_GEOASCII, T_GDAL_NODATA = 34735, 34737, 42113
K_PROJECTEDCSTYPE = 3072  # GeoKey id for the projected CRS


def read_tiff_header(path: Path) -> dict:
    """Parse enough of a (Geo)TIFF to report geometry, dtype and CRS. No pixel reads."""
    info: dict = {"path": str(path), "size_bytes": path.stat().st_size}
    with path.open("rb") as fh:
        head = fh.read(8)
        if len(head) < 8:
            return {**info, "error": "file too short to be a TIFF"}
        if head[:2] == b"II":
            endian = "<"
        elif head[:2] == b"MM":
            endian = ">"
        else:
            return {**info, "error": "not a TIFF (byte-order mark missing)"}
        magic = struct.unpack(endian + "H", head[2:4])[0]
        if magic == 42:
            fmt, off_s = "I", 4
        elif magic == 43:
            return {**info, "error": "BigTIFF not parsed by this stdlib reader", "bigtiff": True}
        else:
            return {**info, "error": f"unexpected TIFF magic {magic}"}
        ifd_off = struct.unpack(endian + fmt, head[4:8])[0]

        tags: dict[int, list] = {}
        while ifd_off:
            fh.seek(ifd_off)
            (n,) = struct.unpack(endian + "H", fh.read(2))
            entry_pos = fh.tell()
            for _ in range(n):
                fh.seek(entry_pos)
                entry = fh.read(12)
                entry_pos = fh.tell()
                tag, typ = struct.unpack(endian + "HH", entry[:4])
                (count,) = struct.unpack(endian + "I", entry[4:8])
                size = TYPE_SIZE.get(typ, 1) * count
                if size <= 4:
                    raw = entry[8:8 + size]
                else:
                    (val_off,) = struct.unpack(endian + "I", entry[8:12])
                    pos = fh.tell()
                    fh.seek(val_off)
                    raw = fh.read(size)
                    fh.seek(pos)
                if typ == 3:
                    vals = list(struct.unpack(endian + f"{count}H", raw))
                elif typ == 4:
                    vals = list(struct.unpack(endian + f"{count}I", raw))
                elif typ == 12:
                    vals = list(struct.unpack(endian + f"{count}d", raw))
                elif typ == 2:
                    vals = raw.split(b"\x00")[0].decode("ascii", "replace")
                else:
                    vals = raw
                tags[tag] = vals
            ifd_off = struct.unpack(endian + "I", fh.read(4))[0] or 0

        def first(tag: int, default=None):
            v = tags.get(tag)
            return v[0] if isinstance(v, list) and v else (v if v is not None else default)

        info["width"] = first(T_IMAGEWIDTH)
        info["height"] = first(T_IMAGELENGTH)
        info["bands"] = len(tags[T_BITSPERSAMPLE]) if T_BITSPERSAMPLE in tags else 1
        info["bits_per_sample"] = tags.get(T_BITSPERSAMPLE, [1] if T_BITSPERSAMPLE not in tags else tags[T_BITSPERSAMPLE])
        sf = tags.get(T_SAMPLEFORMAT, [1] if T_SAMPLEFORMAT not in tags else tags[T_SAMPLEFORMAT])
        fmt_name = {1: "uint", 2: "int", 3: "float"}.get(sf[0] if isinstance(sf, list) else sf, f"sampleformat{sf}")
        info["dtype"] = f"{fmt_name}{info['bits_per_sample'][0] if isinstance(info['bits_per_sample'], list) else info['bits_per_sample']}"
        scale = tags.get(T_MODELPIXELSCALE)
        info["res_x"], info["res_y"] = (scale[0], scale[1]) if scale and len(scale) >= 2 else (None, None)
        tie = tags.get(T_MODELTIEPOINT)
        info["tiepoint"] = tie[:6] if tie else None

        gk = tags.get(T_GEOKEYDIR)
        epsg = None
        if gk and len(gk) >= 8:
            nkeys = gk[3]
            for i in range(nkeys):
                base = 4 + 4 * i
                key_id, loc, cnt, val = gk[base:base + 4]
                if key_id == K_PROJECTEDCSTYPE:
                    epsg = val if loc == 0 else None  # loc != 0 means ASCII continuation: not parsed
        info["epsg"] = epsg
        info["gdal_nodata"] = tags.get(T_GDAL_NODATA) if isinstance(tags.get(T_GDAL_NODATA), str) else None
    return info


def main() -> int:
    DATA.mkdir(exist_ok=True)
    report: dict = {
        "note": "Inspection only. This script does not generate or validate a prize submission.",
        "generated_by": "scripts/prepare_data.py (pure stdlib TIFF header reader)",
        "spec_source": "https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/",
        "data_dir": str(DATA),
        "files": [],
        "missing_documented_names": [],
        "checks": {},
    }
    present = [p for p in sorted(DATA.glob("*.tif")) if not p.name.endswith(".tmp")]
    for name, spec in EXPECTED.items():
        p = DATA / name
        if not p.exists():
            report["missing_documented_names"].append(name)
            continue
        info = read_tiff_header(p)
        checks = {
            "epsg_32611": info.get("epsg") == spec["crs_epsg"],
            "res_100m": info.get("res_x") == spec["res_m"] and info.get("res_y") == spec["res_m"],
        }
        if spec.get("float32_single_band"):
            checks["single_band"] = info.get("bands") == 1
            checks["float32"] = info.get("dtype") == "float32"
        info["checks"] = checks
        info["spec"] = spec
        report["files"].append(info)
    report["checks"]["all_conforming"] = bool(report["files"]) and not report["missing_documented_names"] and all(
        all(f["checks"].values()) for f in report["files"]
    )
    OUT.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    if not present and not report["files"]:
        print("\nNo rasters in data/. Run: bash scripts/download_competition_data.sh", file=sys.stderr)
        return 2
    if report["missing_documented_names"]:
        return 2
    return 0 if report["checks"]["all_conforming"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
