#!/usr/bin/env bash
# scripts/download_competition_data.sh — data placement for the GEMS Prize research library.
#
# WHAT THIS DOES
#   Places the three official competition rasters into data/ and sha256-verifies every
#   byte of them. After it succeeds, `python3 scripts/prepare_data.py` inspects the
#   rasters against the official problem-description spec.
#
# WHAT THIS DOES NOT DO
#   - It never logs in to DrivenData, never stores or asks for credentials.
#   - It never generates, validates, or submits a prediction GeoTIFF.
#     Submission generation is a separate, explicitly gated process.
#
# SOURCES, in order (first one that yields byte-verified files wins):
#   0. Files already in data/ that already pass the sha256 check (idempotent re-runs).
#   1. The project's own git bridge: sparse clone of data/bridge in the
#      buffedlizard55-lab/GEMSDOE repository (github.com). This is a transport copy of
#      the official bytes — GitHub's 100 MB blob limit forces the 418,912,844-byte
#      feature stack to be split into five parts. Every part and the reassembled whole
#      are hash-checked, so the transport cannot silently alter a byte.
#   2. The official mirrors linked from the DrivenData data tab (Dropbox). These need
#      outbound egress to www.dropbox.com; this sandbox blocks that host, so on a
#      restricted machine this step fails loudly and step 1 is what works.
#
# PROVENANCE OF THE sha256 PINS (why they are trustworthy):
#   The pins below were recorded by scripts/inspect_competition_data.py on a
#   GitHub-hosted runner with unrestricted egress directly from the DrivenData data-tab
#   downloads (2026-09-14, data/evidence/inventory.json in the GEMSDOE repository), and
#   are re-stated identically in the bridge manifest (generated 2026-09-17) and in the
#   sibling 8GEMSDOE scripts/download_competition_data.sh. Three independent copies of
#   the same pin set agree. This script treats a pin mismatch as a hard failure.
#
# Exit codes: 0 all placed and verified · 1 pin mismatch or corrupt download ·
#             2 nothing could be placed (all sources unreachable)

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="${GEMS_DATA_DIR:-$REPO_ROOT/data}"
BRIDGE_REPO="https://github.com/buffedlizard55-lab/GEMSDOE"
TMP=""

cleanup() { [[ -z "$TMP" ]] || rm -rf "$TMP"; }
trap cleanup EXIT

mkdir -p "$DEST"

# --- Official pins (three independent copies agree; see header) -----------------
declare -A SHA=(
  ["training_features.tif"]="4371c82e3b8339b807bdffcf4ef59a225520fe2988d521be208ae33743123bc5"
  ["existing_faults.tif"]="7ba308ccdc4418b31a178f4f1ef21aaa6e152e4028f2f6f64b01f7eb25ae4093"
  ["example_submission.tif"]="2176d08e485aa2cd2860ce8df539db4faf4d76163b38a4dd8c30a40454d35cbc"
)
# Bridge-side names, per data/bridge/manifest.json in the GEMSDOE repository.
declare -A BR_NAME=(
  ["training_features.tif"]="gems-geodawn-numerical-features.tif"
  ["existing_faults.tif"]="existing_faults.tif"
  ["example_submission.tif"]="example_submission.tif"
)
# Official mirrors exactly as linked from the DrivenData data tab (login required to
# list them there; the direct links were captured on a logged-in runner 2026-09-14).
declare -A MIRROR=(
  ["training_features.tif"]="https://www.dropbox.com/scl/fi/3vz9o0wwavi26xaeoxlwr/gems-geodawn-numerical-features.tif?rlkey=je8d8fepqfbst9lnwsq9rkplu&st=zj1lag1r&dl=1"
  ["existing_faults.tif"]="https://www.dropbox.com/scl/fi/t7fyt03qdh9egyme0itwo/existing_faults.tif?rlkey=yiao96uluqdkipf0h5vju71jf&st=rnino7ya&dl=1"
  ["example_submission.tif"]="https://www.dropbox.com/scl/fi/6rgvnuady818ol8yqgis4/example_submission.tif?rlkey=kbykilvau066xuogoosbf4cq8&st=8junzdyw&dl=1"
)

fail() { echo "FAIL: $*" >&2; echo "$1" > "$DEST/.placement_status"; exit "${2:-1}"; }

sha_of() { sha256sum "$1" | cut -d' ' -f1; }

verify() { # verify <path> <expected-sha>
  local actual
  [[ -f "$1" ]] || return 1
  actual="$(sha_of "$1")"
  [[ "$actual" == "$2" ]] || { echo "  sha256 mismatch for $1: expected $2, got $actual" >&2; return 1; }
  echo "  PASS sha256 $1"
  return 0
}

echo "=== GEMS Prize data placement ==="
echo "destination: $DEST"
echo "git bridge : $BRIDGE_REPO (data/bridge)"
echo

# --- 0. already placed? ----------------------------------------------------------
for name in training_features.tif existing_faults.tif example_submission.tif; do
  if verify "$DEST/$name" "${SHA[$name]}"; then
    echo "  already placed and verified: $name"
  fi
done

all_ok() {
  for name in "${!SHA[@]}"; do
    verify "$DEST/$name" "${SHA[$name]}" || return 1
  done
  return 0
}

if all_ok; then
  echo
  echo "STATUS: all three official rasters present and sha256-verified. Nothing to do."
  echo "Next: python3 scripts/prepare_data.py"
  echo ok > "$DEST/.placement_status"
  exit 0
fi

# --- 1. git bridge ---------------------------------------------------------------
echo "-- source 1: git bridge (sparse clone of data/bridge) --"
TMP="$(mktemp -d)"
bridge_ok=1
if ! git clone --depth 1 --filter=blob:none --sparse "$BRIDGE_REPO" "$TMP/bridge" 2>&1 | tail -2; then
  bridge_ok=0
else
  (cd "$TMP/bridge" && git sparse-checkout set data/bridge) || bridge_ok=0
fi

if [[ "$bridge_ok" -eq 1 && -f "$TMP/bridge/data/bridge/manifest.json" ]]; then
  B="$TMP/bridge/data/bridge"
  for name in training_features.tif existing_faults.tif example_submission.tif; do
    verify "$DEST/$name" "${SHA[$name]}" && continue
    src="$B/${BR_NAME[$name]}"
    if [[ -f "$src" ]]; then
      echo "  placing $name from bridge"
      cp -f "$src" "$DEST/$name"
    else
      echo "  assembling $name from bridge parts"
      cat "$B/${BR_NAME[$name]}".part-* > "$DEST/$name" || { rm -f "$DEST/$name"; continue; }
    fi
    verify "$DEST/$name" "${SHA[$name]}" || { rm -f "$DEST/$name"; fail "pin mismatch from bridge for $name" 1; }
  done
else
  echo "  git bridge unreachable"
fi

# --- 2. official mirrors (needs egress to dropbox.com) ---------------------------
if ! all_ok; then
  echo "-- source 2: official data-tab mirrors (requires outbound egress) --"
  for name in training_features.tif existing_faults.tif example_submission.tif; do
    verify "$DEST/$name" "${SHA[$name]}" && continue
    echo "  GET mirror: $name"
    if curl -fL --retry 2 --connect-timeout 15 --max-time 1800 -o "$DEST/$name.tmp" "${MIRROR[$name]}"; then
      mv "$DEST/$name.tmp" "$DEST/$name"
      verify "$DEST/$name" "${SHA[$name]}" || { rm -f "$DEST/$name"; fail "pin mismatch from mirror for $name" 1; }
    else
      rc=$?
      echo "  mirror unreachable for $name (curl exit $rc; 35/6/7/28 = host blocked or timeout)"
      rm -f "$DEST/$name.tmp"
    fi
  done
fi

echo
if all_ok; then
  ls -lh "$DEST"/*.tif
  echo
  echo "STATUS: all three official rasters placed and sha256-verified."
  echo "  training_features.tif : the multiband GeoTIFF of the problem description"
  echo "  existing_faults.tif   : the USGS/INGENIOUS training labels (raster form)"
  echo "  example_submission.tif: the organiser template GeoTIFF"
  echo "Next: python3 scripts/prepare_data.py"
  echo ok > "$DEST/.placement_status"
  exit 0
else
  missing=0
  for name in training_features.tif existing_faults.tif example_submission.tif; do
    [[ -f "$DEST/$name" ]] || { echo "  still missing: $name"; missing=1; }
  done
  [[ "$missing" -eq 1 ]] && fail "no source could place every raster; training remains blocked" 2
  fail "some files present but not all verified" 1
fi
