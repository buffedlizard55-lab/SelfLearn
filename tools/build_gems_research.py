#!/usr/bin/env python3
"""Render the GEMS Prize research knowledge base (docs/research/) from
tools/gems_research_content.py.

Idempotent: re-running overwrites the same files with the same bytes (the JSON
exports sort keys; the HTML is fully determined by the content module). It
creates no new site: this section lives inside the existing SelfLearn GitHub
Pages site and links back into it. It also writes an evidence copy of the
anchor register under evidence/gems/.

Usage: python3 tools/build_gems_research.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gems_research_content as C  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "research"
DATA_OUT = OUT / "data"
EVIDENCE_OUT = ROOT / "evidence" / "gems"

STATUS_BADGE = {
    "untested": '<span class="badge">untested</span>',
    "validated-on-spatial-holdout": '<span class="badge ok">validated on spatial holdout</span>',
    "rejected": '<span class="badge err">rejected</span>',
    "open": '<span class="badge warn">open</span>',
    "resolved (documented)": '<span class="badge ok">resolved (documented)</span>',
    "mitigated (methods recorded; re-run tools/verify_links.py from a runner for a fresh machine-readable check)": '<span class="badge info">mitigated - record how to re-check</span>',
    "open (carried) - account-holder awareness only": '<span class="badge warn">open (carried from session 6)</span>',
    "open - needs the account holder to supply or confirm the brief": '<span class="badge warn">open - account holder</span>',
    "open - account-holder cleanup decision (archiving duplicates)": '<span class="badge warn">open - account holder</span>',
}

KIND_BADGE = {
    "official": '<span class="badge ok">official source</span>',
    "internal": '<span class="badge info">internal measurement</span>',
    "published": '<span class="badge">published paper</span>',
    "forum": '<span class="badge info">official forum</span>',
}


def badge(status: str) -> str:
    return STATUS_BADGE.get(status, f'<span class="badge">{status}</span>')


def page(title: str, body: str, depth: int, active: str, description: str) -> str:
    prefix = "../" * depth              # for static assets and links out of the section
    sprefix = "../" * (depth - 1) if depth > 1 else ""   # for links within docs/research/
    rel_nav = [
        ("index.html", "Research home"),
        ("domains/potential-field.html", "Potential-field"),
        ("domains/geomorphology.html", "Geomorphology"),
        ("domains/seismotectonics.html", "Seismotectonics"),
        ("domains/catalogue-gaps.html", "Catalogue gaps"),
        ("domains/prior-art.html", "Prior art"),
        ("domains/governance.html", "Governance"),
        ("hypotheses.html", "Hypotheses"),
        ("data-placement.html", "Data"),
        ("ai-usage-log.html", "AI-usage log"),
        ("changelog.html", "Changelog"),
    ]
    nav = "".join(
        f'<a href="{sprefix}{href}">{label}</a>' if href != active else f'<a href="{sprefix}{href}" aria-current="page">{label}</a>'
        for href, label in rel_nav
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — GEMS Prize research</title>
<meta name="description" content="{description}">
<meta name="color-scheme" content="light dark">
<link rel="stylesheet" href="{prefix}static/style.css">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>&#128506;</text></svg>">
<script>
(function () {{
  try {{
    var stored = localStorage.getItem("selflearn-theme");
    if (stored) document.documentElement.setAttribute("data-theme", stored);
  }} catch (e) {{ }}
}})();
</script>
<script defer src="{prefix}static/app.js"></script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site">
  <div class="wrap">
    <div class="bar">
      <span class="brand">GEMS Prize research <small>knowledge base · DrivenData competition 306 · one entity, one site</small></span>
      <span class="muted small">verified {C.CHECK_DATE} · every claim links its source</span>
    </div>
    <nav class="site" aria-label="Research sections">{nav}<span class="spacer"></span><button class="icon-btn" type="button" data-theme-toggle aria-pressed="false">Light / dark</button></nav>
    <nav class="site" aria-label="Site"><a href="{prefix}index.html">&larr; SelfLearn site overview</a><a href="{prefix}links.html">Official links register</a><a href="{prefix}review.html">For review</a></nav>
  </div>
</header>
<main id="main" class="wrap">
{body}
</main>
<footer class="site"><div class="wrap"><p class="small muted">Built by <span class="mono">tools/build_gems_research.py</span> from
<span class="mono">tools/gems_research_content.py</span> — re-running it reproduces these pages byte for byte.
Generative-AI use for this research is disclosed in the <a href="{sprefix}ai-usage-log.html">AI-usage log</a> (rules &sect;3.2).
No prediction file is generated, validated, or submitted anywhere in this section.</p></div></footer>
</body>
</html>
"""


def entry_html(e: dict) -> str:
    srcs = "".join(
        f'<li><a href="{url}" target="_blank" rel="noopener noreferrer">{label}</a></li>'
        for label, url in e["sources"]
    )
    claims = "".join(f"<li>{c}</li>" for c in e["claims"])
    return f"""
<div class="card" id="{e['id']}">
  <h3>{e['title']} <span class="muted small mono">#{e['id']}</span></h3>
  <p>{KIND_BADGE[e['kind']]}</p>
  <p><strong>Sources:</strong></p><ul>{srcs}</ul>
  <p><strong>What it establishes (quotes verbatim where quoted):</strong></p><ul>{claims}</ul>
  <p><strong>Why it matters here:</strong> {e['relevance']}</p>
  <p><strong>Confidence:</strong> {e['confidence']}</p>
</div>"""


def domain_page(d: dict) -> str:
    entries = "".join(entry_html(e) for e in d["entries"])
    flag = f'<div class="banner warn"><strong>{d["flag"]}</strong></div>' if d["flag"] else ""
    body = f"""
<h1>{d['title']}</h1>
<p class="lede">{d['summary']}</p>
{flag}
{entries}
<p class="small muted"><a href="../hypotheses.html">Hypotheses fed by this domain &rarr;</a></p>"""
    return page(d["title"], body, depth=2, active=f"domains/{d['slug']}.html",
                description=d["summary"])


def index_page() -> str:
    dom_cards = "".join(
        f'<div class="card"><h3><a href="domains/{d["slug"]}.html">{d["title"]}</a></h3>'
        f'<p class="sub">{d["summary"]}</p>'
        + (f'<p><span class="badge warn">{d["flag"]}</span></p>' if d["flag"] else "")
        + f'<p class="small muted">{len(d["entries"])} research entries</p></div>'
        for d in C.DOMAINS
    )
    anchor_rows = "".join(
        f'<tr><td><strong>{a["name"]}</strong><div class="small muted">{a["status"]}</div></td>'
        f'<td><a href="{a["url"]}" target="_blank" rel="noopener noreferrer">{a["url"]}</a></td>'
        f'<td class="small">{a["what"]}</td></tr>'
        for a in C.ANCHORS
    )
    irr_rows = "".join(
        f'<tr><td><span class="mono">{i["id"]}</span></td><td><strong>{i.get("flag", i.get("title", ""))}</strong><div class="small">{i["detail"]}</div></td><td>{badge(i["status"])}</td></tr>'
        for i in C.IRREGULARITIES
    )
    hyp_stats = "".join(
        f'<div class="stat"><span class="n">{sum(1 for h in C.HYPOTHESES if h["status"] == s)}</span>'
        f'<span class="l">{label}</span></div>'
        for s, label in (
            ("validated-on-spatial-holdout", "validated on spatial holdout"),
            ("untested", "untested"),
            ("rejected", "rejected (kept, with why)"),
        )
    )
    body = f"""
<h1>GEMS Prize research &amp; knowledge base</h1>
<p class="lede">Research library for the <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/" target="_blank" rel="noopener noreferrer">Geologic Enhanced Mapping System (GEMS) Prize</a>
(DrivenData competition 306, sponsored by the DOE Office of Geothermal with the National Lab of the Rockies):
identifying faults <em>absent from the existing USGS/INGENIOUS catalogue</em> in the GeoDAWN area.
This section documents and reasons; it does not generate, validate, or submit predictions — those stay behind an
explicit, separate gate. One registered entity, one site: this page lives inside the existing SelfLearn site.</p>

<div class="banner info"><strong>How to read this section.</strong> Every research entry carries its source link,
what the source establishes (verbatim where quoted), why it matters for this competition, and a confidence note.
Verified means: the page was fetched and read on <strong>{C.CHECK_DATE}</strong> (see each anchor's status line), or the
number comes from this project's committed, sha-pinned measurement evidence. Anything short of that is labelled.
The scoring target is Phase-2-style expert review of new faults, so the
<a href="domains/catalogue-gaps.html">catalogue-gap domain</a> is the centrepiece, not a side note.</div>

<div class="grid four">
  <div class="stat"><span class="n">{len(C.ANCHORS)}</span><span class="l">source anchors verified {C.CHECK_DATE}</span></div>
  <div class="stat"><span class="n">{sum(len(d['entries']) for d in C.DOMAINS)}</span><span class="l">research entries across {len(C.DOMAINS)} domains</span></div>
  <div class="stat"><span class="n">{len(C.HYPOTHESES)}</span><span class="l">hypotheses in the backlog</span></div>
  <div class="stat"><span class="n">{len(C.IRREGULARITIES)}</span><span class="l">irregularities flagged</span></div>
</div>

<h2>Research domains</h2>
<div class="grid two">
{dom_cards}
</div>

<h2>Hypothesis backlog</h2>
<div class="grid four">{hyp_stats}</div>
<p>Per hypothesis: layers, physical signature, why it should catch a <em>catalogue gap</em> rather than reproduce a
known fault, expected DTI impact, cost, and status — negative results kept.
<a href="hypotheses.html">Open the backlog &rarr;</a></p>

<h2>Source anchors, verified {C.CHECK_DATE}</h2>
<p class="small muted">These are the addresses this project treats as ground truth for competition facts. Each was
fetched and read on the stated date; where a host is unreachable from one machine, that is recorded rather than
hidden. Machine-readable copy: <a href="data/anchors.json">data/anchors.json</a>.</p>
<div class="table-scroll"><table>
<caption>Status lines describe the fetch that actually happened; none of these rows assert page contents beyond what is quoted on the domain pages.</caption>
<thead><tr><th scope="col">Anchor</th><th scope="col">Address</th><th scope="col">What it verified</th></tr></thead>
<tbody>{anchor_rows}</tbody>
</table></div>

<h2>Compliance (rules &sect;3.2)</h2>
<p>Generative AI is used for this research and disclosed. The dated
<a href="ai-usage-log.html">AI-usage log</a> records what the agent did, with which tools, each session — built
incrementally, not reconstructed at deadline. This section generates no submission file: see the
<a href="data-placement.html">data-placement page</a> for exactly what touched the competition bytes
(hash-verified placement and inspection only).</p>

<h2>Irregularities register</h2>
<p class="small muted">Flagged, never smoothed over. These stay open until the account holder resolves them.</p>
<div class="table-scroll"><table>
<thead><tr><th scope="col">ID</th><th scope="col">Finding</th><th scope="col">Status</th></tr></thead>
<tbody>{irr_rows}</tbody>
</table></div>

<h2>Connected project pages</h2>
<div class="grid two">
  <div class="card"><h3><a href="../index.html">SelfLearn site overview</a></h3>
    <p class="sub">The evidence-verifying research engine this section lives in (docs/, library, review pages).</p></div>
  <div class="card"><h3><a href="https://buffedlizard55-lab.github.io/6GEMSDOE/" target="_blank" rel="noopener noreferrer">6GEMSDOE entry site &mdash; executive summary &amp; submission explainer</a></h3>
    <p class="sub">The existing GEMS entry site: its executive summary, degenerate-baseline measurements, format
    gate, and its own flagged account/repo status. Read-only link from here; this section does not modify it.</p></div>
</div>
"""
    return page("Research home", body, depth=1, active="index.html",
                description="Verified research library and hypothesis backlog for the DOE GEMS Prize challenge.")


def hypotheses_page() -> str:
    rows = ""
    for h in C.HYPOTHESES:
        srcs = ", ".join(
            f'<a href="{url}" target="_blank" rel="noopener noreferrer">{label}</a>' if url.startswith("http") or url.endswith(".html") else label
            for label, url in h["sources"]
        )
        rows += f"""
<div class="card" id="{h['id']}">
  <h3>{h['id']} — {h['title']}</h3>
  <p>{badge(h['status'])}</p>
  <div class="grid two">
    <div>
      <p><strong>Layers:</strong> {h['layers']}</p>
      <p><strong>Physical signature:</strong> {h['signature']}</p>
      <p><strong>Why a catalogue gap, not a known fault:</strong> {h['gap_reasoning']}</p>
    </div>
    <div>
      <p><strong>Expected DTI impact:</strong> {h['dti_impact']}</p>
      <p><strong>Cost:</strong> {h['cost']}</p>
      <p><strong>Status detail:</strong> {h['status_detail']}</p>
      <p class="small"><strong>Evidence:</strong> {srcs}</p>
    </div>
  </div>
</div>"""
    body = f"""
<h1>Hypothesis backlog</h1>
<p class="lede">What this project believes is worth testing to find faults the catalogue missed — each with the
layer, the physical signature, the reasoning for why it should catch a <em>gap</em>, the expected effect on the
distance-weighted Tversky index (DTI), the cost, and the current status. Rejected hypotheses stay here with the
reason. All DTI numbers measured by this project are <strong>mapped-catalogue spatial-CV transfer proxies, not
leaderboard scores</strong>; Phase 2 is judged by geologists reading exactly this style of reasoning.</p>
{rows}
"""
    return page("Hypothesis backlog", body, depth=1, active="hypotheses.html",
                description="Hypothesis backlog with status for the GEMS Prize research project.")


def ai_log_page() -> str:
    entries = ""
    for e in C.AI_LOG:
        tools = "".join(f"<li>{t}</li>" for t in e["tools"])
        actions = "".join(f"<li>{a}</li>" for a in e["actions"])
        notdone = "".join(f"<li>{a}</li>" for a in e["not_done"])
        entries += f"""
<div class="card">
  <h3>{e['date']} — {e['session']}</h3>
  <p><strong>Actor:</strong> {e['actor']}</p>
  <p><strong>Tools used:</strong></p><ul>{tools}</ul>
  <p><strong>What was done:</strong></p><ul>{actions}</ul>
  <p><strong>Explicitly not done:</strong></p><ul>{notdone}</ul>
  <p><strong>Compliance note (rules &sect;3.2):</strong> {e['compliance_notes']}</p>
</div>"""
    body = f"""
<h1>AI-usage log</h1>
<p class="lede">A dated, append-only record of what generative AI did in this research project, kept as a
first-class site artifact so the rules &sect;3.2 disclosure ("indicate in the narrative ... the extent to which,
if any, you used generative AI technology and how you used it") can be written accurately at any moment —
built incrementally, never reconstructed. Plain-text copy: <a href="ai-usage-log.md">ai-usage-log.md</a>.</p>
{entries}
"""
    return page("AI-usage log", body, depth=1, active="ai-usage-log.html",
                description="Dated generative-AI usage log for rules 3.2 compliance.")


def ai_log_md() -> str:
    lines = ["# GEMS Prize research — AI-usage log (rules §3.2)", "",
             "Dated, append-only. Rendered page: docs/research/ai-usage-log.html.", ""]
    for e in C.AI_LOG:
        lines += [f"## {e['date']} — {e['session']}", "",
                  f"Actor: {e['actor']}", "", "Tools used:", *[f"- {t}" for t in e["tools"]],
                  "", "What was done:", *[f"- {a}" for a in e["actions"]],
                  "", "Explicitly not done:", *[f"- {a}" for a in e["not_done"]],
                  "", f"Compliance note (rules §3.2): {e['compliance_notes']}", ""]
    return "\n".join(lines)


def changelog_page() -> str:
    blocks = ""
    for c in C.CHANGELOG:
        items = "".join(f"<li>{i}</li>" for i in c["items"])
        blocks += f'<div class="card"><h3>{c["date"]}</h3><ul>{items}</ul></div>'
    body = f"""
<h1>Changelog</h1>
<p class="lede">What this research section added, newest first. Resumable by design: each session appends its
entry and commits, so an interrupted run leaves a clean state, and re-running the builder reproduces the same
pages.</p>
{blocks}
"""
    return page("Changelog", body, depth=1, active="changelog.html",
                description="Dated changelog of the GEMS research knowledge base.")


def data_placement_page() -> str:
    body = f"""
<h1>Data placement &amp; provenance</h1>
<p class="lede">The one-time blocker for the training pipeline was data placement. It is now cleared
<em>in this repository</em>, with every byte accounted for. This page records exactly what happened and how to
reproduce it.</p>

<div class="banner ok"><strong>Status: placed and verified {C.CHECK_DATE}.</strong>
<code>bash scripts/download_competition_data.sh</code> placed the three official rasters and
<code>python3 scripts/prepare_data.py</code> confirmed they match the official spec. Training itself still needs
a GPU machine; nothing here generates a submission.</div>

<h2>The three files (sha256-pinned)</h2>
<div class="table-scroll"><table>
<thead><tr><th scope="col">File</th><th scope="col">Role (official)</th><th scope="col">Bytes</th><th scope="col">sha256</th></tr></thead>
<tbody>
<tr><td><span class="mono">training_features.tif</span></td><td>the multiband feature GeoTIFF of the problem description</td><td>418,912,844</td><td class="mono small">4371c82e3b8339b807bdffcf4ef59a225520fe2988d521be208ae33743123bc5</td></tr>
<tr><td><span class="mono">existing_faults.tif</span></td><td>training labels (rules &sect;3.3: from the INGENIOUS compilation)</td><td>425,830</td><td class="mono small">7ba308ccdc4418b31a178f4f1ef21aaa6e152e4028f2f6f64b01f7eb25ae4093</td></tr>
<tr><td><span class="mono">example_submission.tif</span></td><td>the organiser submission template</td><td>1,599,597</td><td class="mono small">2176d08e485aa2cd2860ce8df539db4faf4d76163b38a4dd8c30a40454d35cbc</td></tr>
</tbody></table></div>
<p class="small muted">Pin provenance: recorded from the logged-in data tab by a runner-side inventory
(2026-09-14, GEMSDOE <span class="mono">data/evidence/inventory.json</span>), re-stated identically in the GEMSDOE
bridge manifest (2026-09-17) and the 8GEMSDOE placement script, and independently matching the
<span class="mono">training_features_sha256</span> that gemsdoe_review session 6 measured its band identity test
against. Three records, one pin set — and today's placed file matches it.</p>

<h2>Inspection result ({C.CHECK_DATE})</h2>
<div class="table-scroll"><table>
<thead><tr><th scope="col">File</th><th scope="col">Bands</th><th scope="col">dtype</th><th scope="col">Grid</th><th scope="col">CRS</th><th scope="col">Resolution</th><th scope="col">Spec check</th></tr></thead>
<tbody>
<tr><td>training_features.tif</td><td>19</td><td>float32</td><td>3292&times;3730</td><td>EPSG:32611</td><td>100 m</td><td><span class="badge ok">conforming</span></td></tr>
<tr><td>existing_faults.tif</td><td>1</td><td>int8</td><td>3292&times;3730</td><td>EPSG:32611</td><td>100 m</td><td><span class="badge ok">conforming</span></td></tr>
<tr><td>example_submission.tif</td><td>1</td><td>float32</td><td>3292&times;3730</td><td>EPSG:32611</td><td>100 m</td><td><span class="badge ok">conforming (single-band float32 template)</span></td></tr>
</tbody></table></div>
<p class="small muted">19 feature bands matches the problem description's feature list; the single-band label raster
matches the staff clarification in forum thread 11529 (the notebook's "Band 19" printout is an acknowledged
summary-string bug). Machine-readable inventory: <span class="mono">data/inventory.json</span> (gitignored with the
rasters; the committed evidence copy is <span class="mono">evidence/gems/2026-09-26_data_placement.json</span>).</p>

<h2>Sources used, in order</h2>
<ol>
<li>Files already in <span class="mono">data/</span> that pass the sha256 check (idempotent re-runs).</li>
<li>The project's own <strong>git bridge</strong>: a sparse clone of <span class="mono">data/bridge</span> in the
GEMSDOE repository — GitHub's 100 MB blob limit forces the 419 MB feature stack to be split into five parts, each
of which is hash-checked before reassembly.</li>
<li>The official data-tab mirrors (Dropbox links captured from the data tab), used only if the bridge fails and
the machine has egress to the host. This sandbox blocks that host (see the irregularities register), so today's
placement used source 2 (the bridge) — the mirrors stay in the script for unrestricted machines.</li>
</ol>
<p>The script never logs in to DrivenData, never stores credentials, never creates an account, and never writes a
prediction GeoTIFF. <span class="mono">scripts/prepare_data.py</span> inspects headers only (pure standard
library — this repository has no third-party dependencies).</p>

<h2>Reproduce</h2>
<pre>bash scripts/download_competition_data.sh   # places + sha256-verifies data/*.tif (exit 0 = verified)
python3 scripts/prepare_data.py            # header-level inspection vs the official spec (exit 0 = conforming)</pre>
<p class="small muted">After placement, the train&rarr;inference&rarr;validate pipeline is unblocked
<em>modulo compute</em>: training needs a GPU machine; metric, losses and validation already run on CPU.</p>
"""
    return page("Data placement", body, depth=1, active="data-placement.html",
                description="How the official competition rasters were placed and hash-verified.")


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "domains").mkdir(exist_ok=True)

    (OUT / "index.html").write_text(index_page(), encoding="utf-8")
    (OUT / "hypotheses.html").write_text(hypotheses_page(), encoding="utf-8")
    (OUT / "ai-usage-log.html").write_text(ai_log_page(), encoding="utf-8")
    (OUT / "ai-usage-log.md").write_text(ai_log_md(), encoding="utf-8")
    (OUT / "changelog.html").write_text(changelog_page(), encoding="utf-8")
    (OUT / "data-placement.html").write_text(data_placement_page(), encoding="utf-8")
    for d in C.DOMAINS:
        (OUT / "domains" / f"{d['slug']}.html").write_text(domain_page(d), encoding="utf-8")

    write_json(DATA_OUT / "anchors.json", {"checked": C.CHECK_DATE, "anchors": C.ANCHORS})
    write_json(DATA_OUT / "domains.json", C.DOMAINS)
    write_json(DATA_OUT / "hypotheses.json", {"updated": C.CHECK_DATE, "hypotheses": C.HYPOTHESES})
    write_json(DATA_OUT / "ai_usage_log.json", {"rules_section": "3.2", "entries": C.AI_LOG})
    write_json(DATA_OUT / "changelog.json", C.CHANGELOG)
    write_json(DATA_OUT / "irregularities.json", C.IRREGULARITIES)

    # Evidence copies (committed) of this session's verification records.
    write_json(EVIDENCE_OUT / "2026-09-26_anchor_register.json",
               {"kind": "source-anchor verification register; each entry fetched and read on the stated date",
                "checked": C.CHECK_DATE, "anchors": C.ANCHORS})
    print(f"built {len(C.DOMAINS)} domain pages + 6 top pages + JSON exports under {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
