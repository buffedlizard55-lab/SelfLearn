"""The static site builder.

Output goes to ``docs/`` because GitHub Pages can serve a repository directly from
that folder. The site is:

* **static** - no build step, no server, no third-party requests, no fonts or
  scripts loaded from a CDN;
* **readable without JavaScript** - filtering and sorting are enhancements;
* **self-describing** - every page states when it was generated, in which evidence
  mode, and how to verify it by hand.

Colour and layout follow a single stylesheet. Nothing is generated that a reader
cannot trace back to a stored claim, document or experiment.
"""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any, Iterable

from .. import ENGINE_REPO_URL, ENGINE_SITE_URL, __version__
from ..config import EVIDENCE_HIERARCHY, EVIDENCE_LABEL, LIFECYCLE_STATES, SITE_DIR, TOURNAMENT_CRITERIA
from ..util import slugify, utcnow_iso
from . import content
from .assets import SCRIPT, STYLESHEET
from .markdown import render as render_markdown

NAV = (
    ("index.html", "Overview"),
    ("library.html", "Library"),
    ("sources.html", "Sources"),
    ("links.html", "Official links"),
    ("experiments.html", "Experiments"),
    ("method.html", "Method"),
    ("documents.html", "Documents"),
    ("requirements.html", "Requirements"),
    ("review.html", "For review"),
)


# Hand-written repository documents. They live in docs/ as Markdown because the
# evidence column of data/requirements.json points at them by path, and they are
# rendered into a single readable page so the published site carries the same
# text. Nothing here is generated: if a document is missing, the site says so
# instead of showing an empty section.
DOCUMENTS: tuple[tuple[str, str, str, str], ...] = (
    ("DESIGN_SOURCE.md", "design-source", "Design source", "Where the specification came from, and how each part of it was checked."),
    ("ARCHITECTURE.md", "architecture", "Architecture", "Every module, what it does, and why the storage layer is files rather than a database."),
    ("SOURCES.md", "sources-note", "Sources and provenance", "The register of sources, the access rules, and the evidence class of each."),
    ("VERIFICATION.md", "verification", "Verification", "How a claim is tested against a document, and what the verifier cannot see."),
    ("LIMITATIONS.md", "limitations", "Limitations", "Everything this engine does not do, stated plainly."),
    ("ROADMAP.md", "roadmap", "Roadmap", "What is next, in the order it would be built."),
    ("PASSES.md", "passes", "Build passes and audit log", "What was built and reviewed in each pass, including the mistakes found."),
)


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------


def esc(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def link(url: str | None, text: str | None = None, *, class_: str = "") -> str:
    if not url:
        return esc(text or "no link")
    label = esc(text or url)
    cls = f' class="{esc(class_)}"' if class_ else ""
    return f'<a href="{esc(url)}" target="_blank" rel="noopener noreferrer"{cls}>{label}<span aria-hidden="true">&#8599;</span></a>'


def rel(target: str, text: str) -> str:
    return f'<a href="{esc(target)}">{esc(text)}</a>'


def badge(text: str, kind: str = "") -> str:
    return f'<span class="badge {esc(kind)}">{esc(text)}</span>'


def verdict_badge(verdict: str) -> str:
    kind = {"supported": "ok", "partially_supported": "warn", "unsupported": "err", "contradicted": "err"}.get(verdict, "")
    label = {
        "supported": "verified",
        "partially_supported": "partial",
        "unsupported": "failed",
        "contradicted": "contradicted",
    }.get(verdict, verdict)
    return badge(label, kind)


def class_badge(rank: int, label: str) -> str:
    kind = "ok" if rank <= 4 else ("info" if rank <= 6 else "warn")
    return badge(f"{rank}. {label}", kind)


def substance_badge(claim: dict[str, Any]) -> str:
    """The published substance label, with its score, for one claim row."""
    substance = claim.get("substance") or {}
    label = substance.get("label", "")
    if not label:
        return '<span class="muted">unscored</span>'
    kind = {"substantive": "ok", "descriptive": "", "metadata": "warn"}.get(label, "")
    total = substance.get("total")
    text = label if total is None else f"{label} {total:.2f}"
    return badge(text, kind)


def confidence_badge(confidence: str) -> str:
    kind = {"high": "ok", "medium": "info", "low": "warn", "unknown": ""}.get(confidence, "")
    return badge(confidence, kind)


def credential_cell(row: dict[str, Any]) -> str:
    """The credential column: required or optional, and whether it is transmitted.

    A source with no credential says so. A source whose variable is named but whose
    documented mechanism has not been transcribed says that too, because "needs
    key" and "the key would be sent" are different claims.
    """
    if not row:
        return '<span class="muted">open</span>'
    requirement = badge("required", "err") if row.get("required") else badge("optional", "")
    state = row.get("state", "")
    if state == "applied":
        transmitted = badge("transmitted", "ok")
    elif state == "declared_only":
        transmitted = badge("declared, not sent", "warn")
    else:
        transmitted = badge(state or "unknown", "")
    env = f'<span class="mono small">{esc(row.get("env", ""))}</span>'
    detail = esc(row.get("detail", ""))
    return f"{env} {requirement} {transmitted}<div class='small muted'>{detail}</div>"


def pct(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:.1f}%"


def layout(title: str, body: str, *, active: str, data: dict[str, Any], depth: int = 0) -> str:
    prefix = "../" * depth
    nav_parts = []
    for href, label in NAV:
        current = ' aria-current="page"' if href == active else ""
        nav_parts.append(f'<a href="{prefix}{href}"{current}>{esc(label)}</a>')
    nav_items = "".join(nav_parts)
    mode = data.get("mode", "unknown")
    generated = data.get("generated_at", utcnow_iso())
    mode_banner = ""
    if mode == "fixture":
        # Fixture mode has network disabled and replays stored snapshots; it does
        # not load synthetic evidence (load_fixture_evidence has no caller), so
        # the banner must not claim the pages hold no real-world findings.
        mode_banner = (
            '<div class="banner err wrap"><strong>Test run.</strong> This site was generated in fixture mode with '
            "network access disabled: it replays stored snapshots instead of retrieving live, so treat it as "
            "smoke-test output rather than fresh research. Run the engine in live or snapshot mode before "
            "publishing anything from it.</div>"
        )
    elif mode == "snapshot":
        mode_banner = (
            '<div class="banner info wrap"><strong>Snapshot mode.</strong> Live retrieval was unavailable for at least '
            "part of this run, so the claims verified here were checked against the stored documents in "
            "<span class='mono'>evidence/snapshots/</span>. Each claim shows whether it was retrieved live. The source "
            f"status table on the {rel(prefix + 'sources.html', 'sources page')} records which sources were reached.</div>"
        )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} - SelfLearn</title>
<meta name="description" content="SelfLearn: an autonomous research engine that only publishes what it can quote from a retrieved source.">
<meta name="color-scheme" content="light dark">
<script>
/* Applied before the first paint so a stored choice does not flash the other
   theme. Inline and synchronous on purpose; it reads no network and no cookie. */
(function () {{
  try {{
    var stored = localStorage.getItem("selflearn-theme");
    if (stored) document.documentElement.setAttribute("data-theme", stored);
  }} catch (e) {{ /* storage unavailable: fall back to the media query */ }}
}})();
</script>
<link rel="stylesheet" href="{prefix}static/style.css">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>&#128218;</text></svg>">
<script defer src="{prefix}static/app.js"></script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site">
  <div class="wrap">
    <div class="bar">
      <span class="brand">SelfLearn <small>autonomous evidence-verifying research engine v{esc(__version__)}</small></span>
      <span class="muted small">run <span class="mono">{esc(data.get('run_id') or 'n/a')}</span> &middot; generated {esc(generated)} &middot; mode {esc(mode)}</span>
    </div>
    <nav class="site" aria-label="Primary">{nav_items}<span class="spacer"></span><button class="icon-btn" type="button" data-theme-toggle aria-pressed="false">Light / dark</button></nav>
  </div>
</header>
{mode_banner}
<main id="main" class="wrap">
{body}
</main>
<footer class="site">
  <div class="wrap">
    <p><strong>How to check this site.</strong> Every factual statement is a quotation from a document listed on the
    topic page, with a link and a stored copy. Every figure in the generated prose is traceable to a claim or an engine
    computation. The full data behind every page is in <span class="mono">docs/data/</span>. Reproduction steps and
    limitations are on the {rel(prefix + 'method.html', 'method page')}, and every unresolved problem the engine found is
    on the {rel(prefix + 'review.html', 'review page')}.</p>
    <p class="small">Engine and content licence: MIT (code). Retrieved documents keep their own licences, shown against
    each source. Source code: {link(ENGINE_REPO_URL, 'github.com/buffedlizard55-lab/SelfLearn')} &middot;
    Published site: {link(ENGINE_SITE_URL, ENGINE_SITE_URL)} &middot;
    Generated {esc(generated)}. This page contains no third-party scripts, fonts or trackers.</p>
  </div>
</footer>
</body>
</html>
"""


def table(headers: Iterable[str], rows: Iterable[Any], *, caption: str = "", sortable: bool = False, scroll: bool = True) -> str:
    """Render a table from either cell lists or pre-built ``<tr>`` markup.

    Both forms are accepted because a page that needs per-row attributes for the
    client-side filter has to build the row itself. Iterating a row that is
    already a string yields its *characters*, which is how the library page came
    to render every topic as a wall of single-letter cells and left its filter
    matching nothing at all.
    """
    head = "".join(f"<th scope=\"col\">{esc(h)}</th>" for h in headers)
    body_rows = []
    for row in rows:
        if isinstance(row, str):
            body_rows.append(row)
        else:
            cells = "".join(f"<td>{cell}</td>" for cell in row)
            body_rows.append(f"<tr>{cells}</tr>")
    attrs = ' data-sortable' if sortable else ""
    cap = f"<caption>{esc(caption)}</caption>" if caption else ""
    core = f'<table{attrs}>{cap}<thead><tr>{head}</tr></thead><tbody>{"".join(body_rows)}</tbody></table>'
    return f'<div class="table-scroll">{core}</div>' if scroll else core


def topic_slug(meta: dict[str, Any]) -> str:
    """The URL slug of a topic record.

    The slug is carried on the topic record rather than recomputed from the title,
    so a question keeps the same address when its wording is refined.
    """
    return meta.get("slug") or slugify(meta.get("title", "topic"))


def topic_href(meta: dict[str, Any], *, prefix: str = "") -> str:
    """Relative link to a topic page."""
    return f"{prefix}topics/{topic_slug(meta)}.html"


def stat(value: Any, label: str) -> str:
    return f'<div class="stat"><span class="n">{esc(value)}</span><span class="l">{esc(label)}</span></div>'


def card(title: str, body: str, *, sub: str = "", class_: str = "") -> str:
    sub_html = f'<p class="sub">{sub}</p>' if sub else ""
    return f'<div class="card {esc(class_)}"><h3>{esc(title)}</h3>{sub_html}{body}</div>'


def details(summary: str, body: str, *, open_: bool = False) -> str:
    return f"<details{' open' if open_ else ''}><summary>{esc(summary)}</summary>{body}</details>"


def section(title: str, body: str, *, anchor: str = "", note: str = "") -> str:
    anchor_id = f' id="{esc(anchor)}"' if anchor else ""
    note_html = f'<p class="muted small">{note}</p>' if note else ""
    return f'<section class="anchor"{anchor_id}><h2>{esc(title)}</h2>{note_html}{body}</section>'


def bullet_list(items: Iterable[str]) -> str:
    return "<ul>" + "".join(f"<li>{item}</li>" for item in items) + "</ul>"


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------


def page_index(data: dict[str, Any], *, depth: int = 0) -> str:
    counts = data.get("counts", {})
    checks = data.get("checks", {})
    summary = data.get("run_summary", {})
    topics = data.get("topics", [])
    elo = data.get("elo") or {}
    leaderboard = elo.get("leaderboard", [])
    calibration = data.get("calibration") or {}
    thresholds = calibration.get("applied_thresholds") or calibration.get("in_force") or {}

    total_claims = counts.get("claims", 0)
    supported = sum(t.get("statistics", {}).get("supported", 0) for t in topics)
    share = (supported / total_claims) if total_claims else 0.0

    stats = "".join(
        stat(value, label)
        for value, label in (
            (counts.get("topics", 0), "questions under study"),
            (counts.get("claims", 0), "verified claims"),
            (pct(share), "fully supported claims"),
            (counts.get("documents", 0), "documents cited"),
            (counts.get("experiments", 0), "experiments run"),
            (checks.get("irregularity_counts", {}).get("error", 0), "errors flagged for review"),
        )
    )

    intro = f"""
<p class="lede">SelfLearn researches a question by retrieving documents from official APIs, quoting the exact spans it
relies on, and refusing to publish a sentence it cannot trace back to a source. Competing candidate answers are
generated from those verified claims, attacked by rule-based critics, ranked on published criteria, and the losers are
kept.</p>
<div class="banner info"><strong>The rule this project is built around:</strong> a claim is only promoted to
&ldquo;verified&rdquo; when every number and date in it appears in the cited document, and either a verbatim quoted span
is present or the document covers {esc(pct(thresholds.get('supported')))} of the claim's content words. Nothing on this
site is asserted on the basis of a language model's memory.</div>
<div class="grid four" style="margin-top:1rem">{stats}</div>
"""

    what_changed = summary.get("what_changed") or []
    changed_body = bullet_list([esc(item) for item in what_changed]) if what_changed else "<p>Nothing changed since the previous cycle.</p>"

    topic_rows = []
    for topic in sorted(topics, key=lambda t: (-t.get("statistics", {}).get("supported", 0), t["topic"]["topic_id"])):
        meta = topic["topic"]
        statistics = topic.get("statistics", {})
        winner = topic.get("winner")
        topic_rows.append(
            [
                rel(topic_href(meta), meta["title"]),
                esc(meta.get("status", "")),
                f'<span class="num">{statistics.get("claims", 0)}</span>',
                f'<span class="num">{statistics.get("supported", 0)}</span>',
                f'<span class="num">{len(topic.get("questions", []))}</span>',
                esc(winner["persona"]) if isinstance(winner, dict) else '<span class="muted">none declared</span>',
            ]
        )

    leaderboard_rows = [
        [str(row.get("rank")), esc(row.get("key", "")), f'{row.get("rating")}', f'{row.get("wins", 0)}/{row.get("matches", 0)}']
        for row in leaderboard[:12]
    ]

    substance_stats = data.get("substance", {}) or {}
    labels = substance_stats.get("labels", {}) or {}
    substance_rule = data.get("substance_rule", {}) or {}
    cutoffs = substance_rule.get("cutoffs") or {}
    substance_html = (
        f"""<div class="grid four">
{stat(substance_stats.get('claims', 0), 'claims scored')}
{stat(labels.get('substantive', 0), f"substantive (>= {esc(cutoffs.get('substantive'))})")}
{stat(labels.get('descriptive', 0), 'descriptive')}
{stat(labels.get('metadata', 0), f"registry metadata (< {esc(cutoffs.get('metadata'))})")}
</div>"""
        + f"<p class='small muted'>Mean substance score {esc(substance_stats.get('mean_score'))}; "
        f"{substance_stats.get('quantified', 0)} claim(s) carry a quantity and {substance_stats.get('dated', 0)} carry "
        f"a date or year. Where the metadata share is high it is because only registry-style sources were reachable, "
        f"not because the verifier accepted thin claims: see the {rel('sources.html', 'sources page')}.</p>"
    )

    proposals = data.get("topic_proposals", []) or []
    proposal_rows = [
        [
            badge("promoted" if row.get("accepted") else "not promoted", "ok" if row.get("accepted") else ""),
            esc(row.get("title", "")),
            f'<span class="num">{esc(row.get("novelty"))}</span>',
            f'<span class="num">{esc(row.get("importance"))}</span>',
            f'<span class="num">{esc(row.get("potential"))}</span>',
            f'<span class="num">{esc(row.get("total"))}</span>',
            f'<span class="num">{esc(row.get("support_documents", 0))}</span>',
            esc(row.get("reason", "")),
        ]
        for row in proposals
    ]
    proposals_html = (
        table(["Outcome", "Candidate", "Novelty", "Importance", "Potential", "Total", "Docs", "Why"],
              proposal_rows, sortable=True)
        if proposal_rows
        else "<p>No candidate question cleared the promotion gates this cycle. Candidates are proposed only from "
             "documents the engine actually retrieved, and only when the phrase is new to this library and carried by "
             "more than one document.</p>"
    )

    scan = data.get("change_scan", {}) or {}
    scan_rows = [
        [
            f'<span class="mono">{esc(row.get("source_id", ""))}</span>',
            badge(row.get("status", ""), {"scanned": "ok", "unreachable": "err", "error": "err", "skipped": "warn"}.get(row.get("status", ""), "")),
            f'<span class="mono small">{esc((row.get("window") or {}).get("since", ""))} &rarr; {esc((row.get("window") or {}).get("until", ""))}</span>',
            f'<span class="num">{esc(row.get("items_new", 0))}</span>',
            esc((row.get("detail") or "")[:180]),
        ]
        for row in (scan.get("scans") or [])
    ]
    scan_html = (
        table(["Source", "Status", "Window", "New items", "Detail"], scan_rows)
        if scan_rows
        else "<p>No change scan is recorded for this run. The scan needs network access to the source it polls; the "
             "mechanisms and their official documentation are on the "
             + rel("sources.html", "sources page") + ".</p>"
    )

    body = f"""
<h1>An autonomous research library that shows its working</h1>
{intro}

{section("What is being studied right now", table(
    ["Question", "Stage", "Claims", "Verified", "Open questions", "Current best candidate"],
    topic_rows,
    caption="Stages follow the idea lifecycle: new, researching, hypothesis, competing, testing, validated, rejected.",
) + f'<p>{rel("library.html", "Open the full library")} for the per-question pages, or '
  f'{rel("sources.html", "the source register")} for what is being read.</p>', anchor="library")}

{section("This cycle", changed_body + f'<p class="small muted">Generation is idempotent: re-running the engine on '
         f'unchanged inputs reproduces the same records and the same page, which is what makes the diffs reviewable.</p>', anchor="cycle")}

{section("Claim substance across the library", substance_html, anchor="substance",
    note="Verification answers 'is this a span of a document?'. Substance answers 'does it tell me anything?'. The "
         "second is a published arithmetic rule, printed in full on the method page, and it never overrides the first.")}

{section("Questions the engine proposed for itself", proposals_html, anchor="proposals",
    note="Scored as novelty x importance x research potential, all computed from retrieved documents. The candidate "
         "pool is what this engine has retrieved, not an open crawl of the web, so 'novel' means novel to this library.")}

{section("What changed since the last run", scan_html, anchor="scan",
    note="Polled only through filters each operator documents, with the window used recorded. Items found this way "
         "become questions, never claims: nothing here has been verified against a document yet.")}

{section("Competition standings", (
    table(["#", "Brief", "Rating", "Wins / matches"], leaderboard_rows,
          caption="Elo ratings over head-to-head tournament results. Ratings accumulate across cycles and questions."
                  + (f" Wins and matches are counted over the last {esc(elo.get('history_window'))} recorded matches, "
                     "which is all the state file keeps; the ratings themselves are not truncated."
                     if elo.get("history_truncated") else ""))
    if leaderboard_rows else "<p>No tournament has been completed yet.</p>"
), anchor="standings",
   note="Ratings are bookkeeping, not truth. A brief that wins often is a brief that scores well on the published "
        "criteria, which do not include whether the underlying documents are right.")}

{section("Where to look next", f'''
<div class="grid two">
  <div class="card"><h3>To check a fact</h3><p>Open a question from the library. Each fact shows the quoted span, the
  source link, the evidence class, the verification score and the stored copy of what was retrieved.</p>
  <p>{rel("library.html", "Library")}</p></div>
  <div class="card"><h3>To check the reading list</h3><p>Every registered API with its operator, documentation link,
  evidence class, credential requirement and last-run health.</p><p>{rel("sources.html", "Sources")}</p></div>
  <div class="card"><h3>To check the reasoning rules</h3><p>The evidence hierarchy, the verification algorithm, the
  thresholds in force, the tournament weights and which of them are heuristics.</p>
  <p>{rel("method.html", "Method")}</p></div>
  <div class="card"><h3>To find problems</h3><p>Everything the engine could not reconcile: failed sources, missing
  evidence, contradictions, disagreements between its own labels and its own verifier.</p>
  <p>{rel("review.html", "For review")}</p></div>
  <div class="card"><h3>To check the requirements</h3><p>Each requirement from the project brief, line by line, with
  what implements it, how to verify it, and what is not done yet.</p>
  <p>{rel("requirements.html", "Requirements")}</p></div>
  <div class="card"><h3>To re-run it</h3><p>Every experiment shows its command and script hash. The engine itself has
  no dependencies beyond the Python standard library.</p><p>{rel("experiments.html", "Experiments")}</p></div>
</div>
''', anchor="next")}

{section("What this site cannot tell you", bullet_list([f"<strong>{esc(title_)}</strong> &mdash; {text}" for title_, text in content.LIMITATIONS]), anchor="limits",
   note="These limits are part of the deliverable, not a disclaimer. Where a limit can be measured, it is measured; see the method page and the review page.")}
"""
    return layout("Overview", body, active="index.html", data=data, depth=depth)


def page_library(data: dict[str, Any], *, depth: int = 0) -> str:
    topics = data.get("topics", [])
    prefix = "../" * depth
    rows = []
    for topic in sorted(topics, key=lambda t: (-t.get("statistics", {}).get("supported", 0), t["topic"]["topic_id"])):
        meta = topic["topic"]
        statistics = topic.get("statistics", {})
        search = " ".join([meta.get("title", ""), meta.get("question", ""), " ".join(meta.get("keywords", []))]).lower()
        rows.append(
            f'<tr data-row data-kind="{esc(meta.get("status", ""))}" data-search="{esc(search)}">'
            f'<td>{rel(topic_href(meta), meta.get("title", ""))}<div class="small muted">{esc(meta.get("question", ""))}</div></td>'
            f'<td>{badge(meta.get("status", ""), "info")}</td>'
            f'<td class="num">{statistics.get("claims", 0)}</td>'
            f'<td class="num">{statistics.get("supported", 0)}</td>'
            f'<td class="num">{statistics.get("sources", 0)}</td>'
            f'<td class="num">{len(topic.get("questions", []))}</td>'
            f'<td class="num">{len(topic.get("contradictions", []))}</td>'
            "</tr>"
        )
    statuses = sorted({t["topic"].get("status", "") for t in topics})
    options = "".join(f'<option value="{esc(s)}">{esc(s)}</option>' for s in statuses)
    body = f"""
<h1>The library</h1>
<p class="lede">One page per question. Each page holds the verified facts, the competing answers with their scorecards,
the criticism they attracted, the experiments that were run, and the questions the engine decided to ask next. Rejected
ideas stay in the library: their pages keep the reason they were rejected.</p>
<div class="filter">
  <label for="topic-filter" class="small">Filter</label>
  <input id="topic-filter" type="search" placeholder="Filter by title, question or keyword"
         data-filter-target="#topic-table tbody" data-count-target="#topic-count" data-filter-select="#status-filter">
  <label for="status-filter" class="small">Stage</label>
  <select id="status-filter"><option value="">any stage</option>{options}</select>
  <span class="small muted" id="topic-count"></span>
</div>
<div id="topic-table">
{table(["Question", "Stage", "Claims", "Verified", "Sources", "Open questions", "Contradictions"], rows, sortable=True)}
</div>
{section("Idea lifecycle", "<p>Each question advances through the stages below. Nothing is deleted; a question that loses "
         "its evidence returns to an earlier stage and says why.</p>" + bullet_list([esc(s) for s in LIFECYCLE_STATES]),
         anchor="lifecycle")}
"""
    return layout("Library", body, active="library.html", data=data, depth=depth)


def page_topic(topic_data: dict[str, Any], data: dict[str, Any], *, depth: int = 1) -> str:
    meta = topic_data["topic"]
    statistics = topic_data.get("statistics", {})
    prefix = "../" * depth
    claims = topic_data.get("claims", [])
    documents = topic_data.get("documents", [])
    strategies = topic_data.get("strategies", [])
    attacks = topic_data.get("attacks", [])
    questions = topic_data.get("questions", [])
    experiments = topic_data.get("experiments", [])
    contradictions = topic_data.get("contradictions", [])
    tournament = topic_data.get("tournament") or {}
    winner = topic_data.get("winner")
    derived = topic_data.get("derived", [])
    unknowns = topic_data.get("unknowns", [])

    # -- summary block -----------------------------------------------------
    derived_html = (
        "<ul>" + "".join(f"<li>{esc(item['text'])}<div class='small muted'>{esc(item['limitations'])}</div></li>" for item in derived) + "</ul>"
        if derived else "<p>Not enough verified claims yet to report library statistics for this question.</p>"
    )
    unknown_html = (
        "<div class='grid two'>"
        + "".join(
            f"<div class='card unknown'><h3>{esc(item['question'])}</h3><p>{esc(item['answer'])}</p>"
            f"<p class='small muted'><strong>To resolve:</strong> {esc(item['resolve_with'])}</p></div>"
            for item in unknowns
        )
        + "</div>"
        if unknowns
        else "<p>No gaps were detected in the recorded evidence.</p>"
    )

    # -- facts -------------------------------------------------------------
    fact_rows = []
    for claim in claims:
        quote = claim.get("quote") or claim.get("text", "")
        reasons = "".join(f"<li>{esc(reason)}</li>" for reason in claim.get("reasons", [])[:4])
        missing = (
            "<p class='small'><strong>Numbers absent from the document:</strong> "
            + esc(", ".join(claim.get("missing_numbers", [])))
            + "</p>"
            if claim.get("missing_numbers")
            else ""
        )
        substance = claim.get("substance") or {}
        components = substance.get("contributions") or {}
        component_rows = "".join(
            f"<li><span class='mono'>{esc(name)}</span>: {esc(round(value, 3))}</li>"
            for name, value in sorted(components.items())
        )
        substance_detail = (
            f"<p class='small'><strong>Substance {esc(substance.get('total'))} &mdash; "
            f"{esc(substance.get('label', ''))}.</strong> {esc(substance.get('reason', ''))}</p>"
            f"<ul class='small'>{component_rows}</ul>"
            if substance
            else ""
        )
        kind_note = ""
        if claim.get("claim_kind") == "synthesis":
            kind_note = (
                "<p class='small'><strong>Cross-document statement.</strong> Composed from the claims listed in the "
                "synthesis section below; every figure in it appears in one of them.</p>"
            )
        elif claim.get("claim_kind") == "derived":
            kind_note = (
                "<p class='small'><strong>Library computation.</strong> A statement about this library's own records, "
                "not about the world, re-checked from the figures it records.</p>"
            )
        detail = (
            f"<blockquote>{esc(quote)}<cite>{esc(claim['source_name'])} &middot; {link(claim.get('url'), 'source')} "
            f"&middot; snapshot <span class='mono'>{esc(claim.get('evidence_id'))}</span></cite></blockquote>"
            f"<p class='small'>Coverage {esc(pct(claim.get('coverage')))} &middot; verbatim quote match: "
            f"{'yes' if claim.get('quote_match') else 'no'} &middot; recorded {esc(claim.get('recorded_at'))}</p>"
            f"{kind_note}{substance_detail}"
            f"{missing}<ul class='small'>{reasons}</ul>"
        )
        fact_rows.append(
            [
                f'<div id="claim-{esc(claim["claim_id"])}" class="anchor">{esc(claim.get("text", ""))}</div>'
                + details("Show the quoted span, how it was checked, and why it scored this way", detail),
                esc(claim.get("source_name", "")),
                class_badge(int(claim.get("evidence_rank", 9)), claim.get("evidence_class_label", "")),
                verdict_badge(claim.get("verdict", "")),
                substance_badge(claim),
                confidence_badge(claim.get("confidence", "")),
                link(claim.get("url"), "open source"),
            ]
        )

    # -- strategies --------------------------------------------------------
    scorecard_blocks = []
    for strategy in strategies:
        scorecard = strategy.get("scorecard", {}) or {}
        criteria = scorecard.get("criteria", {}) or {}
        criterion_rows = [
            [
                esc(value.get("label", key)),
                f'<span class="num">{value.get("value")}</span>',
                f'<span class="num">{value.get("weight")}</span>',
                badge(value.get("method", ""), "info" if value.get("method") == "measured" else "warn"),
                esc(value.get("detail") or value.get("note", "")),
            ]
            for key, value in criteria.items()
        ]
        is_winner = isinstance(winner, dict) and winner.get("strategy_id") == strategy.get("strategy_id")
        attack_rows = [
            [
                esc(attack.get("critic", "")),
                badge(attack.get("severity", ""), {"fatal": "err", "major": "err", "moderate": "warn", "minor": ""}.get(attack.get("severity", ""), "")),
                esc(attack.get("statement", "")),
                esc(attack.get("outcome", "")),
            ]
            for attack in attacks
            if attack.get("strategy_id") == strategy.get("strategy_id")
        ]
        scorecard_blocks.append(
            f"""<div class="card {'winner' if is_winner else ''}">
<h3>{esc(strategy.get('persona', ''))}{' &mdash; selected by this round' if is_winner else ''}</h3>
<p class="sub">{esc(strategy.get('persona_brief', ''))}</p>
<p><strong>Weighted total:</strong> <span class="num">{esc(scorecard.get('total', 'n/a'))}</span>
{'' if scorecard.get('numbers_checked', True) else badge('unbacked number detected', 'err')}</p>
<div class="bar-meter" role="img" aria-label="score"><span style="width:{max(2, min(100, float(scorecard.get('total') or 0) * 100)):.0f}%"></span></div>
<pre>{esc(strategy.get('argument', ''))}</pre>
{details('Assumptions this brief depends on', bullet_list([esc(a) for a in strategy.get('assumptions', [])]) or '<p>none declared</p>')}
{details('What would falsify it', f"<p>{esc(strategy.get('falsifier', ''))}</p>")}
{details('Scorecard', table(['Criterion', 'Value', 'Weight', 'How', 'Note'], criterion_rows) if criterion_rows else '<p>No scorecard recorded.</p>')}
{details(f'Criticism ({len(attack_rows)})', table(['Rule', 'Severity', 'Attack', 'Outcome'], attack_rows) if attack_rows else '<p>No attacks fired.</p>')}
<p class="small muted">{esc(strategy.get('limitations', ''))}</p>
</div>"""
        )

    # -- questions, contradictions, documents --------------------------------
    question_rows = [
        [esc(q.get("text", "")), badge(q.get("origin", ""), "info"), f'<span class="num">{q.get("priority")}</span>']
        for q in questions
    ]
    contradiction_rows = []
    for item in contradictions:
        contradiction_rows.append(
            [
                esc(item.get("kind", "")),
                badge(item.get("severity", ""), "warn"),
                esc(item.get("detail", "")),
                f'<span class="mono">{esc(item.get("claim_a"))}</span> vs <span class="mono">{esc(item.get("claim_b"))}</span>',
                esc(item.get("resolution", "")),
            ]
        )
    document_rows = [
        [
            esc(doc.get("title", "")),
            esc(doc.get("source_name", "")),
            class_badge(int(doc.get("evidence_rank", 9)), doc.get("evidence_class_label", "")),
            badge("live" if doc.get("is_live") else "snapshot", "ok" if doc.get("is_live") else "warn")
            + (badge("fixture", "err") if doc.get("is_fixture") else ""),
            link(doc.get("url"), "open"),
            f'<span class="mono small">{esc(str(doc.get("content_hash", ""))[:23])}</span>',
        ]
        for doc in documents
    ]
    experiment_rows = [
        [
            esc(exp.get("experiment_id", "")),
            esc(exp.get("hypothesis", "")),
            esc(exp.get("metric", "")),
            f'<span class="num">{esc(exp.get("best_value"))}</span> vs baseline <span class="num">{esc(exp.get("baseline"))}</span>',
            badge(exp.get("status", ""), "ok" if exp.get("status") == "completed" else "warn"),
            f'<span class="mono small">{esc(str(exp.get("script_sha256", ""))[:16])}</span>',
        ]
        for exp in experiments
    ]

    source_status_rows = [
        [
            esc(row.get("source_id", "")),
            esc(row.get("name", "")),
            class_badge(int(row.get("evidence_rank", 9)), row.get("evidence_class", "")),
            badge(row.get("live_status", ""), {"reachable": "ok", "unreachable": "err", "error": "err", "credential_required": "warn"}.get(row.get("live_status", ""), "")),
            esc(row.get("detail", "")),
        ]
        for row in topic_data.get("source_status", [])
    ]

    lifecycle = "".join(
        f'<li class="{ "done" if LIFECYCLE_STATES.index(state) <= LIFECYCLE_STATES.index(meta.get("status", "new")) else "" }">{esc(state)}</li>'
        for state in LIFECYCLE_STATES
        if state != "rejected"
    )

    synthesis = topic_data.get("synthesis", [])
    synthesis_blocks = []
    for item in synthesis:
        citation_rows = [
            [
                f'<span class="mono small">{esc(cite.get("claim_id", ""))}</span>',
                esc(cite.get("text", "")),
                esc(cite.get("source_name", "")),
                verdict_badge(cite.get("verdict", "")),
                link(cite.get("url"), "source"),
            ]
            for cite in item.get("citations", [])
        ]
        synthesis_blocks.append(
            f"""<div class="card">
<p>{esc(item.get('text', ''))}</p>
<p class="small muted">{esc(item.get('limitations', ''))}</p>
{details(f"The {len(citation_rows)} claim(s) this was composed from",
         table(["Claim", "Statement", "Source", "Verification", "Link"], citation_rows)
         if citation_rows else "<p>No citations recorded.</p>")}
</div>"""
        )
    # -- retired statements ------------------------------------------------
    # A statement that an earlier cycle published and a later cycle would no
    # longer produce. It is shown here rather than silently deleted, because a
    # reader who saw it before is entitled to know what happened to it.
    retired = topic_data.get("retired", []) or []
    retired_rows = [
        [
            f'<div id="claim-{esc(item.get("claim_id", ""))}" class="anchor">{esc(item.get("text", ""))}</div>',
            badge(item.get("claim_kind", ""), "info"),
            esc(item.get("superseded", "")),
            esc(item.get("recorded_at", "")),
        ]
        for item in retired
    ]
    retired_html = (
        table(["Statement that was retired", "Kind", "Why", "First published"], retired_rows)
        if retired_rows
        else ""
    )

    substance_stats = topic_data.get("substance", {}) or {}
    substance_note = (
        f"Of the {substance_stats.get('claims', 0)} claim(s) on this page, "
        f"{(substance_stats.get('labels') or {}).get('substantive', 0)} scored as substantive, "
        f"{(substance_stats.get('labels') or {}).get('descriptive', 0)} as descriptive and "
        f"{(substance_stats.get('labels') or {}).get('metadata', 0)} as registry metadata."
    )
    synthesis_html = (
        ("".join(synthesis_blocks) if synthesis_blocks else
         "<p>No cross-document statement could be composed for this question yet. That happens when the verified "
         "claims come from a single document, or when no figure is shared or comparable between two of them.</p>")
        + f"<p class='small muted'>{esc(substance_note)} The scoring rule is published on the "
        f"{rel('../method.html' if depth else 'method.html', 'method page')}.</p>"
    )

    body = f"""
<h1>{esc(meta.get('title', ''))}</h1>
<p class="lede">{esc(meta.get('question', ''))}</p>
<p>
{badge(meta.get('status', ''), 'info')}
{badge(f"origin: {meta.get('origin', 'seed')}")}
{badge(f"claims: {statistics.get('claims', 0)}")}
{badge(f"verified: {statistics.get('supported', 0)}")}
{badge(f"sources: {statistics.get('sources', 0)}")}
<span class="small muted">first seen {esc(meta.get('first_seen', ''))} &middot; last updated {esc(meta.get('last_updated', ''))}</span>
</p>
<ul class="timeline">{lifecycle}</ul>

{section("Summary", f"<p>This section is generated from the library, not from any model's recollection. Every figure in it "
        f"is computed by the engine from the records below.</p>{derived_html}", anchor="summary",
        note="Derived statements about this library. They are re-checked on every cycle; if a recomputation disagrees, the discrepancy is raised on the review page.")}

{section("What we do not know", unknown_html, anchor="unknowns")}

{section("Verified facts", (table(["Statement", "Source", "Evidence class", "Verification", "Substance", "Confidence", "Link"], fact_rows, sortable=True)
        if fact_rows else "<p>No claims have been recorded for this question yet.</p>"),
        anchor="facts",
        note="Ordered most substantive first: a claim carrying a quantity, a period or a mechanism leads, and registry "
             "metadata is labelled as such rather than dressed up as a finding. A statement is listed here only if it "
             "passed the verification check described on the method page; claims that failed stay in the library and "
             "appear on the review page.")}

{section("Cross-document synthesis", synthesis_html, anchor="synthesis",
        note="Statements composed from two or more documents at once. Every figure in one of these must already appear "
             "in a claim it cites, or be a count of documents the engine recorded alongside it: the engine never "
             "averages, sums or extrapolates, and a statement that would need arithmetic is simply not written.")}

{(section("Retired statements", retired_html, anchor="retired",
        note="Published in an earlier cycle, then withdrawn because a re-run of the composition rules no longer "
             "produces them. The library never deletes a record: each statement stays in library/claims.jsonl with "
             "the reason below, and it is excluded from the current facts and synthesis sections and from the audit's "
             "re-verification.")
        if retired_rows else "")}

{section("Competing answers", "".join(scorecard_blocks) if scorecard_blocks else "<p>No candidates have been generated yet.</p>",
        anchor="competition",
        note=(f"Tournament: {esc(tournament.get('round_name', ''))}. " + esc(tournament.get("notes", ""))) if tournament else
             "Candidates are generated only from verified claims; a brief with no usable evidence declares itself blocked instead of guessing.")}

{section("Experiments", (table(["Experiment", "Hypothesis", "Metric", "Result", "Status", "Script hash"], experiment_rows)
        if experiment_rows else "<p>No experiment has been run for this question. The experimental criterion in every "
        "scorecard therefore contributes zero, by construction, until one is.</p>"), anchor="experiments")}

{section("Open questions", (table(["Question", "Origin", "Priority"], question_rows) if question_rows else "<p>None recorded.</p>"),
        anchor="questions",
        note="Questions are derived from what was actually retrieved: hedged findings, missing reference periods, "
             "transfers from other questions, and vocabulary the brief did not contain.")}

{section("Candidate contradictions", (table(["Kind", "Severity", "Why they were flagged", "Claims", "Status"], contradiction_rows)
        if contradiction_rows else "<p>No candidate contradictions were detected on this page.</p>"), anchor="contradictions",
        note="These are candidates for human review, not findings. The engine does not decide which claim is right.")}

{section("Documents used", (table(["Document", "Publisher", "Evidence class", "Retrieval", "Link", "Stored hash"], document_rows)
        if document_rows else "<p>No documents were retrieved for this question.</p>"), anchor="documents",
        note="The stored copy of each document is in evidence/snapshots/, named by the evidence id next to each claim.")}

{section("Source status for this question", (table(["Source", "Name", "Evidence class", "Status", "Detail"], source_status_rows)
        if source_status_rows else "<p>No source status was recorded for this run.</p>"), anchor="sources",
        note="A source that could not be reached is shown here rather than omitted. Unreachable sources are also listed on the review page.")}

{section("Check this page yourself", bullet_list([esc(item) for item in content.REVIEW_CHECKLIST]) +
        f'<p class="small muted">Reproduce the verification stage with <span class="mono">python -m selflearn audit</span>, '
        f'or read the raw data at <span class="mono">docs/data/topics/{esc(topic_slug(meta))}.json</span>.</p>',
        anchor="review")}
"""
    return layout(meta.get("title", "Topic"), body, active="library.html", data=data, depth=depth)


def page_sources(data: dict[str, Any], *, depth: int = 0) -> str:
    sources = data.get("sources", {})
    matrix = sources.get("matrix", [])
    status = {row.get("source_id"): row for row in sources.get("status", [])}
    reliability = {row.get("source_id"): row for row in sources.get("reliability", [])}
    credentials = {row.get("source_id"): row for row in data.get("credentials", []) or []}

    rows = []
    for spec in matrix:
        source_id = spec.get("source_id", "")
        health = status.get(source_id, {})
        rel_row = reliability.get(source_id, {})
        live_status = health.get("live_status", "not_attempted")
        rows.append(
            [
                f'<span class="mono">{esc(source_id)}</span><div class="small">{esc(spec.get("name", ""))}</div>',
                esc(spec.get("operator", "")),
                class_badge(int(spec.get("evidence_rank", 9)), spec.get("evidence_class", "")),
                badge(
                    {"reachable": "reached", "unreachable": "unreachable", "error": "error", "credential_required": "needs key",
                  "not_attempted": "not tried", "robots_disallowed": "refused by robots.txt",
                  "robots_unreachable": "robots.txt unreadable", "adapter_error": "adapter error"}.get(live_status, live_status),
                    {"reachable": "ok", "unreachable": "err", "error": "err", "credential_required": "warn",
                     "robots_disallowed": "err", "robots_unreachable": "warn", "adapter_error": "err"}.get(live_status, ""),
                ),
                credential_cell(credentials.get(source_id, {})),
                link(spec.get("docs_url"), "docs"),
                f'<span class="num">{rel_row.get("documents", 0)}</span>',
                f'<span class="num">{rel_row.get("claims_proposed", 0)}</span>',
                f'<span class="num">{pct(rel_row.get("support_rate")) if rel_row.get("claims_proposed") else "&mdash;"}</span>',
                esc(health.get("detail", "") or spec.get("rate_limit_note", ""))[:220],
            ]
        )

    mechanisms = data.get("change_mechanisms", []) or []
    mechanism_rows = [
        [
            f'<span class="mono">{esc(row.get("source_id", ""))}</span>',
            esc(row.get("label", "")),
            f'<span class="mono small">{esc(row.get("endpoint", ""))}</span>',
            link(row.get("docs_url"), "official documentation"),
            esc(row.get("note", "")),
        ]
        for row in mechanisms
    ]
    scan = data.get("change_scan", {}) or {}
    scan_rows = []
    for row in scan.get("scans", []) or []:
        window = row.get("window", {}) or {}
        scan_rows.append(
            [
                f'<span class="mono">{esc(row.get("source_id", ""))}</span>',
                badge(
                    row.get("status", ""),
                    {"scanned": "ok", "unreachable": "err", "error": "err", "skipped": "warn"}.get(row.get("status", ""), ""),
                ),
                f'<span class="mono small">{esc(window.get("since", ""))} &rarr; {esc(window.get("until", ""))}</span>'
                + (badge("first scan", "warn") if window.get("first_scan") else ""),
                f'<span class="num">{esc(row.get("items_returned", row.get("items_seen", 0)))}</span>',
                f'<span class="num">{esc(row.get("items_out_of_window", 0))}</span>',
                f'<span class="num">{esc(row.get("items_seen", 0))}</span>',
                f'<span class="num">{esc(row.get("items_new", 0))}</span>',
                esc(row.get("detail", ""))[:260],
                f'<span class="mono small">{esc(row.get("request_url", ""))}</span>',
            ]
        )
    scan_items = [
        item
        for row in scan.get("scans", []) or []
        for item in row.get("new_items", []) or []
    ]
    scan_item_rows = [
        [
            esc(item.get("source_id", "")),
            link(item.get("url"), esc((item.get("title") or "untitled")[:120]) or "open"),
            esc(item.get("published_at") or ""),
            esc((item.get("excerpt") or "")[:220]),
        ]
        for item in scan_items[:40]
    ]
    scan_stats = (
        f"Last scan: {esc(scan.get('generated_at', 'not yet run'))} &middot; "
        f"{scan.get('sources_scanned', 0)} of {scan.get('sources_attempted', 0)} sources polled &middot; "
        f"{scan.get('items_seen', 0)} items returned &middot; {scan.get('items_new', 0)} not seen before."
    )
    change_scan_html = (
        (table(["Source", "Status", "Window", "Returned", "Out of window", "Considered", "New", "Detail", "Request"], scan_rows, sortable=True)
         if scan_rows else "<p>No change scan has been recorded yet. Run "
                          "<span class='mono'>python -m selflearn scan</span> from a host with egress.</p>")
        + f"<p class='small muted'>{scan_stats}</p>"
        + (table(["Source", "Item", "Published", "Excerpt"], scan_item_rows,
                 caption="Items the engine had not recorded before. They become questions, not claims: nothing here "
                         "has been verified against a document yet.")
           if scan_item_rows else "")
        + (table(["Source", "Documented change filter", "Endpoint", "Documentation", "Note"], mechanism_rows,
                 caption="Each mechanism is a filter published by the operator of the source.")
           if mechanism_rows else "")
    )

    policy = data.get("robots", {}) or {}
    policy_decisions = policy.get("decisions", []) or []
    policy_hosts = policy.get("hosts", []) or []
    decision_rows = [
        [
            f'<span class="mono">{esc(row.get("host", ""))}</span>',
            f'<span class="mono small">{esc(row.get("path", ""))}</span>',
            badge(
                "allowed" if row.get("allowed") else "refused",
                "ok" if row.get("allowed") else "err",
            ),
            f'<span class="mono small">{esc(row.get("status", ""))}</span>',
            f'<span class="mono small">{esc(row.get("rule", "") or "—")}</span>',
            link(row.get("robots_url"), "robots.txt"),
            f'<span class="small">{esc((row.get("detail") or "")[:300])}</span>',
        ]
        for row in policy_decisions
    ]
    host_rows = []
    for row in policy_hosts:
        note = row.get("media_type_note") or ""
        host_rows.append(
            [
                f'<span class="mono">{esc(row.get("host", ""))}</span>',
                link(row.get("robots_url"), "open"),
                badge(
                    str(row.get("status", "")),
                    {
                        "fetched": "ok",
                        "unavailable": "info",
                        "unreachable": "err",
                        "unreachable_cached": "warn",
                        "offline": "",
                    }.get(str(row.get("status", "")), "warn")
                    if not str(row.get("status", "")).startswith("cached")
                    else "info",
                ),
                f'<span class="num">{esc(row.get("http_status") if row.get("http_status") is not None else "")}</span>',
                f'<span class="mono small">{esc(row.get("content_type", "") or "—")}</span>',
                f'<span class="num">{esc(row.get("rules", 0))}</span>',
                f'<span class="num">{esc(row.get("groups", 0))}</span>',
                f'<span class="mono small">{esc((row.get("sha256") or "").replace("sha256:", "")[:16] or "—")}</span>',
                f'<span class="small">{esc(row.get("fetched_at") or row.get("checked_at") or "")}</span>'
                + (f'<div class="small warn">{esc(note)}</div>' if note else ""),
            ]
        )
    policy_html = (
        (
            f"<p class='small muted'>Checked with user agent <span class='mono'>{esc(policy.get('user_agent', ''))}</span>"
            f" &middot; cache kept for {esc(policy.get('cache_max_age_hours', 24))} hours as the standard asks"
            f" &middot; recorded {esc(policy.get('generated_at', ''))}"
            + (
                f" &middot; decisions made {esc(policy['decisions_recorded_at'])}"
                if policy.get("decisions_recorded_at")
                and policy.get("decisions_recorded_at") != policy.get("generated_at")
                else ""
            )
            + (
                " &middot; this run made no request, so these are the last recorded decisions"
                if not policy.get("network_allowed", True)
                else ""
            )
            + (f" &middot; read from <span class='mono'>{esc(policy.get('source'))}</span>" if policy.get("source") else "")
            + "</p>"
        )
        if policy.get("hosts_published") or policy.get("hosts_checked") or policy.get("decisions")
        else ""
    )
    if decision_rows:
        policy_html += table(
            ["Host", "Path requested", "Decision", "Status", "Rule that matched", "The operator's file", "Why"],
            decision_rows,
            sortable=True,
            caption=(
                "One row per request URL the engine would send. A refusal means no request was made: the engine "
                "obeys the operator's own file rather than working around it."
            ),
        )
    if host_rows:
        policy_html += table(
            ["Host", "robots.txt", "Fetch result", "HTTP", "Content type", "Rules", "Groups", "sha256 (first 16)", "Fetched"],
            host_rows,
            sortable=True,
            caption=(
                "What each operator's robots.txt answered. A media type that is not text/plain is recorded, because "
                "the standard requires text/plain and a body that is not a robots file parses to no rules at all."
            ),
        )
    if not decision_rows and not host_rows:
        policy_html += (
            "<p>No access-policy check has been recorded yet. Run "
            "<span class='mono'>python3 -m selflearn robots</span>, or any research cycle, and the decisions appear "
            "here with the rule that produced each one.</p>"
        )

    counts = {
        "total": len(matrix),
        "reached": sum(1 for row in status.values() if row.get("live_status") == "reachable"),
        "unreachable": sum(1 for row in status.values() if row.get("live_status") in {"unreachable", "error"}),
        "refused": sum(1 for row in status.values() if str(row.get("live_status", "")).startswith("robots_")),
        "needs_key": sum(1 for spec in matrix if spec.get("requires_key")),
    }

    body = f"""
<h1>Sources</h1>
<p class="lede">Every source the engine is allowed to read, with the body that operates it, the official documentation,
the evidence class it can contribute, whether it needs a credential, and whether the last run actually reached it.</p>
<div class="grid four">
{stat(counts['total'], 'registered sources')}
{stat(counts['reached'], 'reached this run')}
{stat(counts['unreachable'], 'unreachable this run')}
{stat(counts['refused'], 'refused by robots.txt')}
{stat(counts['needs_key'], 'require a free key')}
</div>
<div class="banner info"><strong>Rules for admission.</strong> A source is registered only if it is operated by the body
that owns the data, or by a non-profit that publishes the authoritative index. Aggregators of unknown provenance are not
registered. A source that needs a credential is listed but never called without one, and appears as
&ldquo;needs key&rdquo; rather than being quietly absent. Wikipedia is registered as a secondary compilation and is used
only for orientation; it is never the grounds for a factual claim.</div>

{section("The register", table(
    ["Source", "Operated by", "Evidence class", "Last run", "Credential", "Documentation", "Docs", "Claims", "Support rate", "Rate limit / detail"],
    rows, sortable=True, caption="Support rate is the share of claims from that source that passed full verification."),
    anchor="register")}

{section("Access policy: what each operator's robots.txt allows", policy_html, anchor="policy",
    note="The engine treats itself as a crawler and obeys "
         + link("https://www.rfc-editor.org/rfc/rfc9309.html", "RFC 9309, the Robots Exclusion Protocol")
         + " literally: the most specific rule wins (2.2.2), an allow beats an equivalent disallow, a 4xx robots.txt "
           "means the whole host is available (2.3.1.3), and an unreachable robots.txt means complete disallow "
           "(2.3.1.4). A route refused here was never requested, and the refusal is published with the verbatim rule.")}

{section("Change scanning: what is new since the last run", change_scan_html, anchor="changes",
    note="Only sources whose operator documents a change filter are scanned. A source with no documented filter is "
         "reported as having none rather than being polled and having its whole result set described as new. Each "
         "mechanism links to the operator's own documentation.")}

{section("What to do about a source that fails", bullet_list([
    "Unreachable sources are reported on the review page with the transport error, so the gap is visible.",
    "A source that repeatedly returns HTTP errors is a candidate for a fix in the adapter, not for silent removal.",
    "Credentials are read from environment variables named in the table. The engine never stores a credential in the repository.",
    "Run <span class='mono'>python -m selflearn credentials</span> to list every keyed source, whether its variable is "
    "set, and the operator's own page for requesting one.",
]), anchor="failures")}
"""
    return layout("Sources", body, active="sources.html", data=data, depth=depth)


#: What each register field is for, in the reader's own words.
LINK_FIELD_LABEL = {
    "docs_url": "API documentation",
    "key_url": "Where a free key is issued",
    "license_url": "Licence",
    "terms_url": "Terms of use",
    "citation": "Citation in this project's prose",
}


def _link_row(
    url: str,
    *,
    source_id: str,
    operator: str,
    purpose: str,
    result: dict[str, Any] | None,
) -> str:
    """One row of the official-link register, with the outcome the check recorded."""
    if result is None:
        outcome = badge("not checked", "warn")
        detail = "Not present in the committed link check."
        kind = "unchecked"
    elif result.get("ok"):
        status = result.get("status")
        outcome = badge(f"resolved {status}", "ok")
        final_url = result.get("final_url") or ""
        redirected = final_url and final_url.rstrip("/") != (url or "").rstrip("/")
        detail = (
            "Redirected to " + link(final_url, "the address it landed on") if redirected else "Resolved directly."
        )
        kind = "resolved"
    else:
        status = result.get("status")
        label = f"HTTP {status}" if status else "unreachable"
        outcome = badge(label, "err")
        detail = esc((result.get("error") or "no detail recorded")[:200])
        kind = "failed"
    search = " ".join([source_id, operator, purpose, url]).lower()
    return (
        f'<tr data-row data-kind="{esc(kind)}" data-search="{esc(search)}">'
        f'<td><span class="mono">{esc(source_id)}</span><div class="small muted">{esc(operator)}</div></td>'
        f"<td>{esc(purpose)}</td>"
        f"<td>{link(url, 'open')}</td>"
        f"<td>{outcome}</td>"
        f'<td class="small">{detail}</td>'
        "</tr>"
    )


def page_links(data: dict[str, Any], *, depth: int = 0) -> str:
    """Every URL this project publishes, with the outcome of the last check.

    The point of the page is manual review: a reader who wants to check a source
    for themselves should not have to hunt for the address, and should be told
    honestly whether the address was reachable when the engine last looked, and
    from where.
    """
    check = data.get("link_check") or {}
    sources = data.get("sources", {})
    matrix = {row.get("source_id"): row for row in sources.get("matrix", [])}
    by_source: dict[str, list[dict[str, Any]]] = check.get("by_source", {}) or {}
    credentials = data.get("credentials", []) or []

    # Every URL the register publishes, matched to the outcome recorded for it.
    rows: list[str] = []
    seen: set[str] = set()
    for source_id, results in sorted(by_source.items()):
        spec = matrix.get(source_id, {})
        operator = spec.get("operator", "")
        for result in sorted(results, key=lambda r: (str(r.get("group")), str(r.get("url")))):
            url = result.get("url") or ""
            if url in seen:
                continue
            seen.add(url)
            purpose = LINK_FIELD_LABEL.get(result.get("field", ""), result.get("group", "link"))
            if result.get("group") == "prose":
                operator = "this repository"
                purpose = f"cited in {esc(source_id)}"
            elif result.get("group") == "change_mechanism":
                purpose = "Documented change filter"
            rows.append(
                _link_row(url, source_id=source_id, operator=operator, purpose=purpose, result=result)
            )

    total = len(rows)
    resolved = sum(1 for row in rows if 'data-kind="resolved"' in row)
    failed = sum(1 for row in rows if 'data-kind="failed"' in row)
    unchecked = sum(1 for row in rows if 'data-kind="unchecked"' in row)
    sources_covered = len({r.split('data-search="')[1].split(" ")[0] for r in rows if "data-search=" in r})

    if not check.get("available"):
        provenance = (
            '<div class="banner warn"><strong>No link check is committed.</strong> '
            + esc(check.get("detail", ""))
            + " The addresses below are the ones the register publishes; none of them has been resolved by a run this "
            "repository has recorded.</div>"
        )
    else:
        provenance = (
            '<div class="banner info"><strong>Where these statuses came from.</strong> Recorded '
            f"{esc(check.get('generated_at', 'at an unrecorded time'))} by "
            f"<span class='mono'>{esc(check.get('label', 'an unlabelled run'))}</span>. "
            "A status of <em>unreachable</em> means the machine that ran the check could not open a TLS connection to "
            "that host. It is not a statement that the page is gone, which is why the machine is named: a sandbox with "
            "restricted egress and a runner with unrestricted egress will disagree, and both records are true of the "
            "machine that made them.</div>"
        )

    credential_rows = []
    for row in credentials:
        mechanism = row.get("mechanism")
        if mechanism:
            shape = (
                f'<span class="mono">{esc(mechanism["name"])}: {esc(mechanism["prefix"])}&lt;value&gt;</span>'
                if mechanism["kind"] == "header"
                else f'<span class="mono">?{esc(mechanism["name"])}=&lt;value&gt;</span>'
            )
            citation = link(mechanism.get("docs_url"), "operator's page")
            quote = mechanism.get("quote") or ""
            checked_on = mechanism.get("verified_at") or ""
            evidence = (
                f'<blockquote>{esc(quote)}<cite>{citation}'
                + (f" &middot; read {esc(checked_on)}" if checked_on else " &middot; not re-read this pass")
                + "</cite></blockquote>"
                if quote
                else f"<p class='small muted'>Applied by <span class='mono'>{esc(mechanism.get('applied_by', ''))}</span>.</p>"
            )
        else:
            shape = '<span class="muted">not transcribed</span>'
            evidence = (
                "<p class='small muted'>The operator's documented mechanism has not been transcribed, so no credential "
                "is sent. The source is used within its unauthenticated limits.</p>"
            )
        state_badge = {
            "applied": badge("transmitted", "ok"),
            "declared_only": badge("declared, not sent", "warn"),
        }.get(row.get("state", ""), badge(row.get("state", ""), ""))
        credential_rows.append(
            [
                f'<span class="mono">{esc(row.get("source_id"))}</span><div class="small">{esc(row.get("name"))}</div>',
                f'<span class="mono">{esc(row.get("env"))}</span>'
                + (badge("required", "err") if row.get("required") else badge("optional", "")),
                shape,
                state_badge,
                link(row.get("key_url"), "request a key"),
                evidence,
            ]
        )

    body = f"""
<h1>Official links, and how each one was checked</h1>
<p class="lede">Every address this project publishes: the operator's own documentation, licence and key-request page for
each registered source, the documentation behind each change filter, and the citations in this repository's prose. Each
row carries the outcome of the last recorded check, so a reviewer can go straight to the primary source and see whether
the engine could reach it.</p>
<div class="grid four">
{stat(total, 'URLs published')}
{stat(resolved, 'resolved')}
{stat(failed, 'did not resolve')}
{stat(sources_covered, 'sources and files covered')}
</div>
{provenance}
<div class="banner warn"><strong>What this check proves, and what it does not.</strong> It records the HTTP status and
the address after redirects. It does not read the page, so it cannot say the page still says what this project took
from it. Where the engine relies on an operator's exact words - the credential mechanisms below - the words are quoted
here beside the link, with the date they were read, so that part can be checked by eye.</div>

<div class="filter">
  <label for="link-filter" class="small">Filter</label>
  <input id="link-filter" type="search" placeholder="Filter by source, operator or address"
         data-filter-target="#link-table tbody" data-count-target="#link-count" data-filter-select="#outcome-filter">
  <label for="outcome-filter" class="small">Outcome</label>
  <select id="outcome-filter">
    <option value="">any outcome</option>
    <option value="resolved">resolved</option>
    <option value="failed">did not resolve</option>
    <option value="unchecked">not checked</option>
  </select>
  <span class="small muted" id="link-count"></span>
</div>
<div id="link-table">
{table(["Source", "What the address is for", "Address", "Last check", "Detail"], rows, sortable=True,
       caption="Status and final address only. Page content is never asserted here.")}
</div>

{section("Credentials: what each operator documents, and what the engine sends", table(
    ["Source", "Variable", "Documented mechanism", "State", "Key", "The operator's own words"], credential_rows,
    caption="A variable can be set and still never reach the request. The state column is the difference."),
    anchor="credentials",
    note="Every mechanism below is transcribed from the operator's own page, quoted beside it, with the date it was "
         "read. A source whose mechanism has not been transcribed is published as 'declared, not sent' rather than "
         "being guessed at: the engine will not invent an authentication scheme. "
         "Run <span class='mono'>python3 -m selflearn credentials</span> for the same table as JSON.")}

{section("Re-running the check", bullet_list([
    "<span class='mono'>python3 tools/verify_links.py</span> - resolve every published URL from this machine and "
    "write <span class='mono'>reports/link_check.json</span>.",
    "<span class='mono'>python3 tools/verify_links.py --label &lt;where it ran&gt;</span> - record the machine, "
    "because a result is only interpretable together with the egress that produced it.",
    "<span class='mono'>python3 tools/link_check_changed.py</span> - report whether any URL changed outcome, which is "
    "what decides whether a fresh report is worth committing.",
    "The Tests workflow runs the check on every push from a runner with unrestricted egress and commits the register "
    "when an outcome moves.",
]), anchor="rerun")}
"""
    return layout("Official links", body, active="links.html", data=data, depth=depth)


def page_experiments(data: dict[str, Any], *, depth: int = 0) -> str:
    experiments = data.get("experiments", [])
    catalogue = data.get("experiment_catalogue", [])
    rows = []
    for exp in experiments:
        result = exp.get("result_json", {}) or {}
        checks = result.get("checks", []) or []
        check_html = "".join(
            f"<li>{badge('passed' if c.get('outcome') else 'failed', 'ok' if c.get('outcome') else 'err')} {esc(c.get('check'))} "
            f"<span class='small muted'>{esc(c.get('observed'))}</span></li>"
            for c in checks
        )
        rows.append(
            [
                f'<span class="mono">{esc(exp.get("experiment_id"))}</span><div class="small muted">seed {esc(exp.get("seed"))}</div>',
                esc(exp.get("hypothesis", "")),
                esc(exp.get("metric", "")),
                f'<span class="num">{esc(exp.get("baseline"))}</span> &rarr; <span class="num">{esc(exp.get("best_value"))}</span>'
                + f'<div class="small muted">best variant: {esc(exp.get("best_variant"))}</div>',
                badge(exp.get("status", ""), "ok" if exp.get("status") == "completed" else "warn"),
                details("Reproduce", f"<pre>{esc(exp.get('command', ''))}</pre>"
                        f"<p class='small'>Script: <span class='mono'>{esc(exp.get('script_path'))}</span><br>"
                        f"sha256: <span class='mono'>{esc(exp.get('script_sha256'))}</span></p>"),
                f"<ul class='small'>{check_html}</ul>" if check_html else "<span class='muted small'>no checks recorded</span>",
            ]
        )

    catalogue_rows = [
        [
            f'<span class="mono">{esc(spec.get("experiment_id"))}</span>',
            esc(spec.get("title")),
            badge(spec.get("purpose"), "info"),
            esc(spec.get("hypothesis")),
            esc(spec.get("falsifier")),
            f'<span class="mono small">{esc(spec.get("run_command"))}</span>',
        ]
        for spec in catalogue
    ]

    body = f"""
<h1>Experiments</h1>
<p class="lede">An experiment produces the strongest evidence class in the hierarchy: a result this engine measured
itself, with the script, the seed, the command and the full output stored next to it. Anybody can re-run it and compare.</p>
<div class="banner warn"><strong>Scope.</strong> The catalogue is computational. These experiments can test statements
about algorithms, numerics and the engine's own verification procedure. They cannot test statements about the physical
world; that needs measured data from a registered source. Where a question needs such data and none is available, the
engine says so instead of attaching an unrelated benchmark to it. Every experiment is labelled
<em>capability</em> (it proves the pipeline works end to end) or <em>method</em> (it validates the engine's own
procedure).</div>

{section("Results this run", table(
    ["Experiment", "Hypothesis", "Metric", "Baseline &rarr; best", "Status", "Reproduce", "Checks"], rows) if rows else
    "<p>No experiment has been run yet in this deployment.</p>", anchor="results")}

{section("Catalogue", table(
    ["Id", "Title", "Purpose", "Hypothesis", "Falsifier", "Command"], catalogue_rows), anchor="catalogue")}
"""
    return layout("Experiments", body, active="experiments.html", data=data, depth=depth)


def page_method(data: dict[str, Any], *, depth: int = 0) -> str:
    calibration = data.get("calibration") or {}
    thresholds = calibration.get("applied_thresholds") or calibration.get("in_force") or {}
    baseline_thresholds = calibration.get("baseline", {}).get("thresholds", {}) if isinstance(calibration.get("baseline"), dict) else {}
    selected = calibration.get("selected") or {}

    hierarchy_rows = [
        [str(rank), esc(name), esc(description), "yes" if rank <= 5 else "no"]
        for rank, name, description in EVIDENCE_HIERARCHY
    ]
    criteria_rows = [
        [
            esc(label),
            f'<span class="num">{weight}</span>',
            badge("measured" if key not in {"scalability"} else "heuristic", "ok" if key not in {"scalability"} else "warn"),
            esc(note),
        ]
        for key, label, weight, note in TOURNAMENT_CRITERIA
    ]
    rules = [
        ("C1", "citation", "A cited claim did not pass full verification.", "fatal"),
        ("C2", "citation", "A cited claim is only partially supported.", "moderate"),
        ("C3", "assumption", "The brief states an assumption it has not evidenced.", "minor"),
        ("C4", "counterexample", "Another claim in the library pulls the other way.", "major"),
        ("C5", "repro", "The claim rests on a stored snapshot rather than a live retrieval.", "moderate"),
        ("C6", "repro", "The claim rests on synthetic fixture evidence.", "fatal"),
        ("C7", "data", "All cited claims come from a single source.", "major"),
        ("C8", "data", "The freshest cited document is more than three years old.", "moderate"),
        ("C9", "assumption", "A mechanism is inferred from observational statements.", "major"),
        ("C10", "simplicity", "More assumptions than cited claims.", "moderate"),
        ("C11", "simplicity", "Long argument relative to the evidence cited.", "minor"),
    ]
    rule_rows = [[esc(r), esc(t), esc(d), badge(s, {"fatal": "err", "major": "err", "moderate": "warn"}.get(s, ""))] for r, t, d, s in rules]

    memory_rows = [[esc(name), f'<span class="mono small">{esc(path)}</span>', esc(desc)] for name, path, desc in content.MEMORY_LAYERS]

    calibration_rows = []
    for row in calibration.get("grid", [])[:40]:
        calibration_rows.append(
            [
                f'<span class="num">{row.get("supported")}</span>',
                f'<span class="num">{row.get("partially_supported")}</span>',
                f'<span class="num">{row.get("quote_min_chars")}</span>',
                f'<span class="num">{row.get("accuracy")}</span>',
                f'<span class="num">{row.get("macro_f1")}</span>',
                f'<span class="num">{row.get("false_supports")}</span>',
            ]
        )

    substance_rule = data.get("substance_rule", {}) or {}
    substance_weight_rows = [
        [
            f'<span class="mono">{esc(name)}</span>',
            f'<span class="num">{esc(weight)}</span>',
            esc((substance_rule.get("features") or {}).get(name, "")),
        ]
        for name, weight in (substance_rule.get("weights") or {}).items()
    ]
    substance_cutoffs = substance_rule.get("cutoffs") or {}
    substance_label_rows = [
        [badge(name, {"substantive": "ok", "descriptive": "", "metadata": "warn"}.get(name, "")), esc(text)]
        for name, text in (substance_rule.get("labels") or {}).items()
    ]
    substance_stats = data.get("substance", {}) or {}
    substance_rule_html = (
        table(["Feature", "Weight", "What it tests"], substance_weight_rows,
              caption="Weights sum to 1, so the score reads directly as a share of the maximum.")
        + table(["Label", "Meaning"], substance_label_rows,
                caption=f"Cut-offs: substantive at {esc(substance_cutoffs.get('substantive'))} and above, "
                        f"metadata below {esc(substance_cutoffs.get('metadata'))}.")
        + f"<p class='small muted'>{esc(substance_rule.get('note', ''))} This run: "
        f"{substance_stats.get('claims', 0)} claim(s) scored, "
        f"{(substance_stats.get('labels') or {}).get('substantive', 0)} substantive, "
        f"{(substance_stats.get('labels') or {}).get('descriptive', 0)} descriptive, "
        f"{(substance_stats.get('labels') or {}).get('metadata', 0)} metadata; mean score "
        f"{esc(substance_stats.get('mean_score'))}.</p>"
    )

    synthesis_rule_html = """
<ol>
<li>Only claims that already passed verification against their own document take part, and only direct quotations -
never the engine's own computed statistics.</li>
<li>A statement must cite at least two <em>documents</em>. Two claims from one document are not a cross-document
statement, and none is written.</li>
<li>Every figure in the statement must appear in one of the cited claims, or be a count of documents or sources the
engine computed and recorded beside the statement. There is no averaging, no summing, no extrapolation and no unit
conversion anywhere in this stage: the arithmetic that would produce such a figure is simply never performed.</li>
<li>Disagreement is published as disagreement. When two documents carry different values that share a unit word, the
statement names both figures, says the engine cannot decide, and links both sources.</li>
<li>The audit recomputes every synthesis statement from its citations on each cycle. If a cited claim is withdrawn or
edited, the recomputation fails and the finding is raised rather than the statement being quietly kept.</li>
</ol>
<p class="small muted">The unit in a range or divergence statement is the word that followed the number in the source
sentence. Two documents using the same word for different measures would be combined, which is why those statements are
published as needing review rather than as findings.</p>
"""

    invention_rule = data.get("invention_rule", {}) or {}
    invention_gates = invention_rule.get("gates") or {}
    invention_rule_html = (
        f"<p><strong>Formula.</strong> <span class='mono'>{esc(invention_rule.get('formula', ''))}</span></p>"
        + bullet_list([
            f"<strong>Novelty</strong> &mdash; {esc(invention_rule.get('novelty', ''))}",
            f"<strong>Importance</strong> &mdash; {esc(invention_rule.get('importance', ''))}",
            f"<strong>Potential</strong> &mdash; {esc(invention_rule.get('potential', ''))}",
            f"<strong>Candidate pool</strong> &mdash; {esc(invention_rule.get('candidate_pool', ''))}",
        ])
        + table(["Gate", "Value"], [
            ["Minimum documents carrying the phrase", f'<span class="num">{esc(invention_gates.get("min_documents"))}</span>'],
            ["Minimum novelty", f'<span class="num">{esc(invention_gates.get("min_novelty"))}</span>'],
            ["Minimum total score", f'<span class="num">{esc(invention_gates.get("min_total"))}</span>'],
            ["Maximum promotions per cycle", f'<span class="num">{esc(invention_gates.get("max_promotions_per_cycle"))}</span>'],
        ], caption="All three gates must hold before a candidate becomes a question.")
    )

    body = f"""
<h1>Method</h1>
<p class="lede">Everything the engine does to a document, and everything it is forbidden from doing. If you only read one
page of this project, read this one and then the review page.</p>

{section("The evidence hierarchy", table(
    ["Rank", "Class", "What it means", "Can ground a fact?"], hierarchy_rows,
    caption="Rank 1 is the strongest. A claim inherits the rank of the document it was extracted from."),
    anchor="hierarchy",
    note="Claims from ranks 6 and below (secondary compilations, commentary, unverified assertions) are recorded but never presented as established facts.")}

{section("How a claim becomes verified", f'''
<ol>
<li>An adapter retrieves a document from a registered API and stores the exact bytes plus a sha256 of the text.</li>
<li>Sentences are cut out of that text. A sentence is only a candidate if it has at least four discriminating words
(negations, hedges, units and numbers are kept).</li>
<li>The claim is checked against the document it came from:
  <ul>
    <li>every numeric literal in the claim must appear in the document, after canonicalising thousands separators,
        trailing zeros and the many spellings of &ldquo;percent&rdquo;;</li>
    <li>every date and year must appear in the document;</li>
    <li>the passage that overlaps the claim most must not differ in polarity (a negation present in one and absent in
        the other is a hard failure);</li>
    <li>a verbatim quoted span of at least {esc(thresholds.get('quote_min_chars'))} characters, if present, is accepted as
        support on its own;</li>
    <li>otherwise the share of the claim's content words present in the document must reach
        {esc(thresholds.get('supported'))} for full support, or {esc(thresholds.get('partially_supported'))} to be kept and
        labelled as needing review.</li>
  </ul>
</li>
<li>The verdict, the coverage score and the reason for it are stored with the claim and shown on the topic page.</li>
<li>On every cycle the audit stage re-runs this check against the stored document and reports any claim whose verdict
changed. A claim that fails is never deleted; it stays visible and is counted.</li>
</ol>
<p><strong>What no language model does here.</strong> Steps 1 to 5 involve no model at all. They are string and set
operations over bytes the engine retrieved, which is why they can be re-run and why their failure modes can be
inspected.</p>
''', anchor="verification")}

{section("Thresholds in force", f'''
<p>These are the values actually used for every claim on this site. They are not fixed assumptions: they are re-derived
each cycle from a labelled case set, by the calibration experiment below.</p>
<table>
<thead><tr><th>Setting</th><th>Value in force</th><th>Configured default</th></tr></thead>
<tbody>
<tr><td>Support threshold (content words present in the document)</td><td class="num">{esc(thresholds.get('supported'))}</td><td class="num">{esc(baseline_thresholds.get('supported', 'n/a'))}</td></tr>
<tr><td>Partial-support threshold</td><td class="num">{esc(thresholds.get('partially_supported'))}</td><td class="num">{esc(baseline_thresholds.get('partially_supported', 'n/a'))}</td></tr>
<tr><td>Minimum quotable span, characters</td><td class="num">{esc(thresholds.get('quote_min_chars'))}</td><td class="num">{esc(baseline_thresholds.get('quote_min_chars', 'n/a'))}</td></tr>
</tbody></table>
<p class="small muted">Calibrated {esc(calibration.get('ran_at', 'not yet run'))} against {esc(calibration.get('case_count', 'n/a'))} labelled cases.
Accuracy at the selected point: {esc((selected or {}).get('accuracy', 'n/a'))}; false supports: {esc((selected or {}).get('false_supports', 'n/a'))}.
Selection rule: {esc(calibration.get('objective', 'n/a'))}.</p>
{details('Show the sweep grid', table(['Support', 'Partial', 'Quote chars', 'Accuracy', 'Macro F1', 'False supports'], calibration_rows) if calibration_rows else '<p>No calibration has been recorded.</p>')}
''', anchor="thresholds")}

{section("How candidates compete", table(
    ["Criterion", "Weight", "How it is computed", "Definition"], criteria_rows,
    caption="Weights sum to 1. The total is a weighted mean over the criteria that could be evaluated."),
    anchor="criteria",
    note="Heuristic criteria are labelled so that a reader can discard them. The experimental criterion contributes zero until an experiment exists for the question, which is stated on the question's page.")}

{section("How a claim is judged substantive", substance_rule_html, anchor="substance",
    note="The score changes reading order and labels metadata. It never changes a verification verdict: a claim that "
         "failed verification is ranked below an equivalent claim that passed, and nothing is dropped.")}

{section("How a cross-document statement is allowed to be written", synthesis_rule_html, anchor="synthesis-rule")}

{section("How a new question is proposed", invention_rule_html, anchor="invention",
    note="The candidate pool is what this engine has already retrieved, not an open crawl of the web. 'Novel' means "
         "novel to this library. That narrowing is published wherever a proposed question appears, because the "
         "alternative - inventing subjects from the engine's own vocabulary - is the failure mode this project exists "
         "to avoid.")}

{section("What the critic looks for", table(
    ["Rule", "Type", "Trigger", "Severity"], rule_rows), anchor="critic",
    note="Attacks talk about the analysis, never about the world. A candidate carrying an unresolved fatal attack cannot win its round.")}

{section("Memory", table(["Layer", "Where it lives", "What it holds"], memory_rows), anchor="memory")}

{section("What the engine refuses to do", bullet_list([esc(item) for item in content.REFUSALS]), anchor="refusals")}

{section("How to verify this project by hand", bullet_list([f"<strong>{esc(t)}</strong> &mdash; {b}" for t, b in content.HOW_TO_VERIFY]), anchor="verify")}

{section("Limitations", bullet_list([f"<strong>{esc(t)}</strong> &mdash; {b}" for t, b in content.LIMITATIONS]), anchor="limitations")}

{section("Requirements traceability", f'<p>Each requirement from the project brief is traced line by line, with what '
        f'implements it and how to check it: {rel("requirements.html", "the requirements matrix")}.</p>', anchor="requirements")}
"""
    return layout("Method", body, active="method.html", data=data, depth=depth)


def page_requirements(data: dict[str, Any], *, depth: int = 0) -> str:
    requirements = data.get("requirements", [])
    rows = []
    for item in requirements:
        status = item.get("status", "unknown")
        kind = {"implemented": "ok", "partial": "warn", "planned": "info", "out of scope": ""}.get(status, "")
        evidence = "<br>".join(
            f'<span class="mono small">{esc(e)}</span>' for e in item.get("evidence", [])
        )
        rows.append(
            [
                f'<span class="mono">{esc(item.get("id"))}</span>',
                esc(item.get("requirement", "")),
                badge(status, kind),
                evidence,
                esc(item.get("how_to_verify", "")),
                esc(item.get("gap", "")),
            ]
        )
    counts: dict[str, int] = {}
    for item in requirements:
        counts[item.get("status", "unknown")] = counts.get(item.get("status", "unknown"), 0) + 1

    body = f"""
<h1>Requirements</h1>
<p class="lede">The project brief, decomposed line by line, with the status of each line, what implements it, and how a
reader can check that claim. Where a line is not fully met, the gap is stated rather than implied.</p>
<div class="grid four">
{stat(counts.get('implemented', 0), 'implemented')}
{stat(counts.get('partial', 0), 'partially implemented')}
{stat(counts.get('planned', 0), 'planned')}
{stat(counts.get('out of scope', 0), 'out of scope')}
</div>
<div class="banner info">The design document this project follows is an external shared conversation:
{link(content.DESIGN_DOC_URL, 'Design Autonomous Research System')}. Section numbers below refer to that document.</div>

{section("The matrix", table(
    ["Id", "Requirement", "Status", "What implements it", "How to verify", "Gap"], rows, sortable=True,
    caption="Statuses are updated by hand when the code changes; they are not computed, and a wrong status is a bug worth reporting."),
    anchor="matrix")}
"""
    return layout("Requirements", body, active="requirements.html", data=data, depth=depth)


def page_review(data: dict[str, Any], *, depth: int = 0) -> str:
    irregularities = data.get("irregularities", [])
    failures = data.get("failures", [])
    contradictions = data.get("contradictions", [])
    checks = data.get("checks", {})
    calibration = data.get("calibration") or {}

    def severity_order(row: dict[str, Any]) -> tuple[int, str]:
        return ({"error": 0, "warning": 1, "info": 2}.get(row.get("severity", "info"), 3), row.get("stage", ""))

    def irregularity_row(item: dict[str, Any]) -> list[str]:
        return [
            badge(item.get("severity", ""), {"error": "err", "warning": "warn"}.get(item.get("severity", ""), "info")),
            esc(item.get("stage", "")),
            f'{esc(item.get("summary", ""))}<div class="small muted mono">{esc(item.get("irregularity_id", ""))}</div>',
            esc(item.get("detail", ""))[:400],
            link(item.get("url"), "link") if item.get("url") else "&mdash;",
            esc(item.get("suggested_action", "")),
            esc(item.get("created_at", "")),
        ]

    open_irregularities = sorted((i for i in irregularities if not i.get("resolved")), key=severity_order)
    resolved_irregularities = sorted((i for i in irregularities if i.get("resolved")), key=severity_order)
    irregularity_rows = [irregularity_row(item) for item in open_irregularities]
    # A resolved finding keeps its original text; the reviewer's reason sits
    # beside it, never in place of it.
    resolved_irregularity_rows = [
        irregularity_row(item)[:4]
        + [
            # Records written before the reviewer fields existed (the topic
            # rejections of 2026-09-21) carry the reason in `detail`; say so
            # rather than claiming no reason was recorded.
            esc(item.get("resolution", ""))
            or ("<span class='muted'>closed when recorded; the reason is the detail column</span>"
                if item.get("stage") == "review" else "<span class='muted'>no reason recorded</span>"),
            (link(item.get("resolution_link"), "reference") if item.get("resolution_link") else "&mdash;"),
            esc(item.get("resolved_at", "")) or esc(item.get("created_at", "")) or "&mdash;",
        ]
        for item in resolved_irregularities
    ]
    failure_rows = [
        [esc(item.get("stage", "")), esc(item.get("summary", "")), esc(item.get("detail", ""))[:300], esc(item.get("remedy", ""))]
        for item in failures
    ]

    def contradiction_row(item: dict[str, Any]) -> list[str]:
        return [
            esc(item.get("topic_id", "")),
            f'{esc(item.get("kind", ""))}<div class="small muted mono">{esc(item.get("contradiction_id", ""))}</div>',
            esc(item.get("detail", "")),
            f'<span class="mono">{esc(item.get("claim_a", ""))}</span> / <span class="mono">{esc(item.get("claim_b", ""))}</span>',
        ]

    open_contradictions = [c for c in contradictions if c.get("resolution", "unresolved") == "unresolved"]
    resolved_contradictions = [c for c in contradictions if c.get("resolution", "unresolved") != "unresolved"]
    contradiction_rows = [contradiction_row(item) for item in open_contradictions]
    resolved_contradiction_rows = [
        contradiction_row(item)
        + [
            esc(item.get("resolution_note", "")) or "<span class='muted'>no reason recorded</span>",
            (link(item.get("resolution_link"), "reference") if item.get("resolution_link") else "&mdash;"),
            esc(item.get("resolved_at", "")) or "&mdash;",
        ]
        for item in resolved_contradictions
    ]
    disagreements = calibration.get("disagreements") or []
    disagreement_rows = [[esc(d.get("case_id")), esc(d.get("name")), esc(d.get("expected")), esc(d.get("predicted"))] for d in disagreements]

    body = f"""
<h1>For review</h1>
<p class="lede">This page is the point of the project: everything the engine could not reconcile on its own. Each entry
says what was found, where, and what would resolve it. Nothing here is a conclusion.</p>
<div class="grid four">
{stat(checks.get('irregularity_counts', {}).get('error', 0), 'open errors')}
{stat(checks.get('irregularity_counts', {}).get('warning', 0), 'open warnings')}
{stat(checks.get('unresolved_contradictions', 0), 'unresolved contradictions')}
{stat(len(resolved_irregularities) + len(resolved_contradictions), 'resolved by a reviewer')}
</div>
<div class="banner info"><strong>How to act on this page.</strong> An entry is either a genuine problem in the engine
(a source that moved, a parser that broke, a threshold that is wrong) or a genuine problem in the evidence (sources
disagree, or a claim cannot be checked). The suggested action states which. Reproduce the whole audit with
<span class="mono">python -m selflearn audit</span> and read the machine-readable list in
<span class="mono">docs/data/irregularities.json</span>.</div>

{section("Irregularities", table(
    ["Severity", "Stage", "Finding", "Detail", "Link", "Suggested action", "Detected"], irregularity_rows, sortable=True)
    if irregularity_rows else "<p>No irregularities are open.</p>", anchor="irregularities",
    note="Open findings only. A reviewer closes one with <span class='mono'>python3 tools/resolve_finding.py --id &lt;id&gt; --reason ...</span>; "
         "the record is appended to, never edited, and the engine carries the decision forward if it detects the same finding again.")}

{section("Label disagreements", table(
    ["Case", "Name", "Human label", "Engine verdict"], disagreement_rows) if disagreement_rows else
    "<p>The verifier agrees with every human label in the calibration set, except the cases documented as engine "
    "limitations, which are listed on the method page.</p>", anchor="labels",
    note="These are the cases where the engine's verdict differs from a hand-written label. They are the most informative rows on this page.")}

{section("Candidate contradictions", table(
    ["Question", "Kind", "Why it was flagged", "Claims"], contradiction_rows) if contradiction_rows else
    "<p>No candidate contradictions are open.</p>", anchor="contradictions")}

{section("Resolved by a reviewer", (
    (table(["Severity", "Stage", "Finding", "Detail", "Reviewer's reason", "Reference", "Resolved"], resolved_irregularity_rows)
     if resolved_irregularity_rows else "<p>No irregularity has been resolved by a reviewer.</p>")
    + (table(["Question", "Kind", "Why it was flagged", "Claims", "Reviewer's reason", "Reference", "Resolved"], resolved_contradiction_rows)
       if resolved_contradiction_rows else "<p>No contradiction has been resolved by a reviewer.</p>")
    ), anchor="resolved",
    note="The original finding is shown unchanged next to the reason a reviewer gave for closing it. Reopen one with "
         "<span class='mono'>python3 tools/resolve_finding.py --id &lt;id&gt; --reopen --reason ...</span>.")}

{section("Failures", table(["Stage", "Failure", "Detail", "Remedy"], failure_rows) if failure_rows else
    "<p>No stages failed in this run.</p>", anchor="failures")}

{section("Open an issue", f'''<p>Found something wrong? The most useful reports name a claim id or an evidence id from a
topic page, because those identifiers resolve directly to a stored document and a stored verdict.</p>
{bullet_list([
  f"{link(ENGINE_REPO_URL + '/issues/new', 'Open an issue')} with the claim id and what you expected to see.",
  "If a link is dead, the source adapter needs fixing; the review page will list the transport error after the next run.",
  "If a claim looks wrong but passed verification, that is a finding worth reporting: it means the verification check has a blind spot, and there is a test fixture waiting for a counterexample.",
])}
''', anchor="issues")}
"""
    return layout("For review", body, active="review.html", data=data, depth=depth)


def page_documents(rendered: list[dict[str, Any]], data: dict[str, Any], *, depth: int = 0) -> str:
    """One page holding every hand-written repository document.

    The Markdown files stay in ``docs/`` (they are cited as evidence in
    ``data/requirements.json``); this page renders the same bytes so a reader of
    the published site never has to leave it. A document that is missing from the
    repository is reported as missing rather than silently omitted.
    """
    if not rendered:
        body = section(
            "Repository documents",
            '<p class="banner warn">No document files were found next to the site. Run '
            '<span class="mono">python3 -m selflearn site</span> from the repository root.</p>',
        )
        return layout("Documents", body, active="documents.html", data=data, depth=depth)

    toc_items = []
    sections = []
    for doc in rendered:
        if doc["missing"]:
            sections.append(
                section(
                    doc["title"],
                    f'<p class="banner warn">The file <span class="mono">{esc(doc["file"])}</span> is not present in '
                    "this checkout, so its text cannot be shown. It is listed here so the gap is visible rather than "
                    "hidden.</p>",
                    anchor=doc["anchor"],
                )
            )
            continue
        toc_items.append(f'<li>{rel("#" + doc["anchor"], doc["title"])} &middot; <span class="muted small">{esc(doc["summary"])}</span></li>')
        headings = "".join(
            f'<li class="lvl-{level}">{rel("#" + doc["anchor"] + "-" + anc, title)}</li>'
            for level, anc, title in doc["headings"]
            if level <= 3
        )
        sections.append(
            section(
                doc["title"],
                f'<p class="sub">{esc(doc["summary"])}</p>'
                f'<p class="muted small">Source file: <span class="mono">{esc(doc["file"])}</span> '
                f'&middot; {link(doc["raw_url"], "read the raw Markdown on GitHub")}</p>'
                f'<nav class="toc" aria-label="Contents of {esc(doc["title"])}"><ol class="toc-list">{headings}</ol></nav>'
                f'<div class="doc">{doc["html"]}</div>',
                anchor=doc["anchor"],
            )
        )

    body = (
        section(
            "Repository documents",
            "<p>These documents are written by hand and committed to the repository. The requirements table cites them "
            "as evidence, so the site shows the same text rather than a summary of it. Every heading below links to the "
            "raw file, and the raw file is what the requirements table points at.</p>"
            f'<nav class="toc" aria-label="Documents"><ol class="toc-list">{"".join(toc_items)}</ol></nav>',
        )
        + "".join(sections)
    )
    return layout("Documents", body, active="documents.html", data=data, depth=depth)


def page_not_found(data: dict[str, Any]) -> str:
    body = f"<h1>Page not found</h1><p>The page you asked for is not part of this site. Start from the {rel('index.html', 'overview')} or the {rel('library.html', 'library')}.</p>"
    return layout("Not found", body, active="", data=data, depth=0)


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------


def root_shell(title: str, description: str, body: str, data: dict[str, Any]) -> str:
    """Shared shell for the two files GitHub Pages serves from the branch root.

    Pages publishes this repository from the branch root while the engine writes
    the site into ``docs/``. These pages therefore sit one level above it and link
    its stylesheet rather than carrying their own copy, so the entry point and the
    site cannot drift apart visually.
    """
    generated = data.get("generated_at") or ""
    run_id = data.get("run_id") or "no run recorded"
    mode = data.get("mode") or "unknown"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<meta name="color-scheme" content="light dark">
<link rel="stylesheet" href="docs/static/style.css">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>&#128218;</text></svg>">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site">
  <div class="wrap">
    <div class="bar">
      <span class="brand">SelfLearn <small>autonomous evidence-verifying research engine v{esc(__version__)}</small></span>
      <span class="muted small">run <span class="mono">{esc(run_id)}</span> &middot; generated {esc(generated)} &middot; mode {esc(mode)}</span>
    </div>
  </div>
</header>
<main id="main" class="wrap">
{body}
</main>
<footer class="site">
  <div class="wrap">
    <p class="small">Source code: {link(ENGINE_REPO_URL, 'github.com/buffedlizard55-lab/SelfLearn')} &middot;
    Research site: {rel('docs/index.html', 'docs/index.html')} &middot; Generated {esc(generated)}.
    No third-party scripts, fonts or trackers.</p>
  </div>
</footer>
</body>
</html>
"""


def page_root_entry(data: dict[str, Any]) -> str:
    """The repository-root landing page that GitHub Pages serves."""
    counts = data.get("counts") or {}
    checks = data.get("checks") or {}
    topics = data.get("topics") or []
    link_check = data.get("link_check") or {}
    credentials = data.get("credentials", []) or []

    topic_items = "".join(
        f'<li>{rel(topic_href(item["topic"], prefix="docs/"), item["topic"].get("title", "question"))} '
        f'<span class="muted small">- {esc((item.get("topic") or {}).get("status", ""))}</span></li>'
        for item in topics[:8]
    )

    pages = (
        ("docs/index.html", "Overview", "What the engine is studying, and what changed this cycle."),
        ("docs/library.html", "Library", "One page per question: the verified facts, the competing answers, the criticism."),
        ("docs/sources.html", "Sources", "Every registered source, who operates it, and whether the last run reached it."),
        ("docs/links.html", "Official links", "Every published address, with the outcome of the last check."),
        ("docs/method.html", "Method", "Evidence hierarchy, thresholds in force, scoring criteria, refusals."),
        ("docs/documents.html", "Documents", "Design source, architecture, verification, limits, roadmap."),
        ("docs/requirements.html", "Requirements", "The brief traced line by line against the implementation."),
        ("docs/review.html", "For review", "Every unresolved irregularity, failure and contradiction."),
    )
    page_cards = "".join(
        f'<div class="card"><h3>{rel(href, label)}</h3><p class="sub">{esc(blurb)}</p></div>'
        for href, label, blurb in pages
    )

    link_note = (
        f"{esc(link_check.get('ok', 0))} of {esc(link_check.get('checked', 0))} published URLs resolved, "
        f"checked {esc(link_check.get('generated_at', 'at an unrecorded time'))} by "
        f"<span class='mono'>{esc(link_check.get('label', 'an unlabelled run'))}</span>."
        if link_check.get("available")
        else "No link check is committed yet; the addresses are published but none has been resolved by a recorded run."
    )
    transmitted = sum(1 for row in credentials if row.get("state") == "applied")
    declared_only = sum(1 for row in credentials if row.get("state") == "declared_only")

    irregularity_counts = checks.get("irregularity_counts") or {}
    open_errors = irregularity_counts.get("error", 0)
    open_warnings = irregularity_counts.get("warning", 0)

    body = f"""
<h1>An autonomous research engine that shows its working</h1>
<p class="lede">SelfLearn researches a question by retrieving documents from official public APIs, cutting its claims
out of those documents as exact spans, and refusing to publish a sentence it cannot trace back to a stored source. No
language model is used at any stage: the accept/reject decision is a string and set comparison a reviewer can re-run.</p>

<div class="grid four">
{stat(counts.get("topics", 0), 'questions under study')}
{stat(counts.get("claims", 0), 'verified claims')}
{stat(counts.get("documents", 0), 'documents cited')}
{stat(open_errors, 'errors open for review')}
</div>

<div class="banner info"><strong>The rule this project is built around.</strong> A claim is promoted to
&ldquo;verified&rdquo; only when every number and date in it appears in the cited document, and either a verbatim
quoted span is present or the document covers the claim's content words above a published threshold. Anything the
engine could not do is published too: unreachable sources, missing credentials, contradictions and its own
irregularities. {esc(open_warnings)} warning(s) and {esc(open_errors)} error(s) are currently listed on the
{rel('docs/review.html', 'review page')}.</div>

<h2>Read the research</h2>
<div class="grid two">
{page_cards}
</div>

<h2>Provenance you can check</h2>
<div class="grid two">
  <div class="card"><h3>Official sources</h3>
    <p class="sub">{link_note}</p>
    <p class="small">Every address is the operator's own page. {rel('docs/links.html', 'See the register')}.</p></div>
  <div class="card"><h3>Credentials</h3>
    <p class="sub">{esc(transmitted)} source(s) have a credential the adapter actually transmits;
    {esc(declared_only)} name a variable whose mechanism has not been transcribed and are published as
    &ldquo;declared, not sent&rdquo;.</p>
    <p class="small">{rel('docs/links.html#credentials', 'What each operator documents')}.</p></div>
</div>

<h2>Questions currently under research</h2>
{f'<ul>{topic_items}</ul>' if topic_items else '<p class="muted">No topics are active in the stored library.</p>'}

<h2>Check it yourself</h2>
<p>Every figure on the site is traceable to a claim or to a count the engine recorded. The stored bytes behind each
claim, the calibration that set the verification thresholds, the experiment results and the run summary are all
committed to the repository.</p>
<ul class="muted small">
  <li><code>python3 -m selflearn audit</code> - re-verify every stored claim from its snapshot</li>
  <li><code>python3 tools/check_claim.py</code> - one claim, its document, its hash, a fresh re-check</li>
  <li><code>python3 -m selflearn credentials</code> - which keyed sources are enabled, and how to enable them</li>
  <li><code>python3 tools/verify_links.py</code> - resolve every URL this project publishes</li>
  <li><code>python3 -m selflearn selftest</code> - the test suite, no network and no credentials required</li>
</ul>
<p><a class="cta" href="docs/index.html">Open the research site &rarr;</a></p>
"""
    return root_shell(
        "SelfLearn - autonomous evidence-verifying research engine",
        "SelfLearn researches questions from public sources and publishes only what it can quote from a retrieved document.",
        body,
        data,
    )


def page_root_not_found(data: dict[str, Any]) -> str:
    """The 404 Pages serves from the branch root.

    Pages looks for ``404.html`` at the site root. For this repository that is the
    branch root, so the copy the engine writes into ``docs/`` would never be shown;
    this one is written beside the entry point and points back into the site.
    """
    body = """
<h1>That page is not part of this site</h1>
<p class="lede">The address you asked for does not exist here. Nothing was removed to produce this page: the engine
only adds and annotates records, and a topic that is closed keeps its page and the reason it was closed.</p>
<div class="grid two">
  <div class="card"><h3>Start again</h3>
    <p class="sub">The entry point, or straight into the research.</p>
    <p><a href="index.html">Landing page</a> &middot; <a href="docs/index.html">Overview</a> &middot;
    <a href="docs/library.html">Library</a></p></div>
  <div class="card"><h3>Or check the record</h3>
    <p class="sub">Everything the engine could not do is published rather than hidden.</p>
    <p><a href="docs/review.html">For review</a> &middot; <a href="docs/links.html">Official links</a> &middot;
    <a href="docs/method.html">Method</a></p></div>
</div>
"""
    return root_shell(
        "Page not found - SelfLearn",
        "This page does not exist on the SelfLearn site. Start from the overview or the library.",
        body,
        data,
    )


def render_documents(source_dir: Path | None = None, *, repo_url: str = ENGINE_REPO_URL) -> list[dict[str, Any]]:
    """Read and render the hand-written documents that sit beside the site."""
    base = Path(source_dir) if source_dir is not None else SITE_DIR
    rendered: list[dict[str, Any]] = []
    for filename, anchor, title, summary in DOCUMENTS:
        path = base / filename
        entry: dict[str, Any] = {
            "file": f"docs/{filename}",
            "anchor": anchor,
            "title": title,
            "summary": summary,
            "raw_url": f"{repo_url}/blob/main/docs/{filename}",
            "missing": not path.exists(),
            "html": "",
            "headings": [],
        }
        if path.exists():
            body, headings = render_markdown(path.read_text(encoding="utf-8"))
            entry["html"] = body
            entry["headings"] = headings
        rendered.append(entry)
    return rendered



def build_site(
    data: dict[str, Any],
    out_dir: Path,
    *,
    write_data: bool = True,
    write_root_entry: bool = False,
) -> list[Path]:
    """Write the whole site. Returns the list of files written.

    ``write_root_entry`` also writes the GitHub Pages entry point next to the site
    directory (the repository root), because Pages publishes this repository from
    the branch root while the site itself lives in ``docs/``.
    """
    out = Path(out_dir)
    static = out / "static"
    topics_dir = out / "topics"
    data_dir = out / "data"
    for path in (out, static, topics_dir, data_dir):
        path.mkdir(parents=True, exist_ok=True)

    written: list[Path] = []

    def write(path: Path, body: str) -> None:
        path.write_text(body, encoding="utf-8")
        written.append(path)

    rendered_docs = render_documents()
    write(static / "style.css", STYLESHEET)
    write(static / "app.js", SCRIPT)
    write(out / ".nojekyll", "")
    if write_root_entry:
        # Pages serves the repository root; these two files make the URL a doorway to
        # the site rather than a bare directory listing.
        root = out.parent
        (root / "index.html").write_text(page_root_entry(data), encoding="utf-8")
        # Pages looks for 404.html at the *site* root, which for this repository is
        # the branch root, not docs/. Without this file the copy in docs/ is
        # unreachable and a mistyped address falls back to GitHub's own page.
        (root / "404.html").write_text(page_root_not_found(data), encoding="utf-8")
        (root / ".nojekyll").write_text("", encoding="utf-8")
        written.extend([root / "index.html", root / "404.html", root / ".nojekyll"])
    write(out / "index.html", page_index(data))
    write(out / "library.html", page_library(data))
    write(out / "sources.html", page_sources(data))
    write(out / "links.html", page_links(data))
    write(out / "experiments.html", page_experiments(data))
    write(out / "method.html", page_method(data))
    write(out / "documents.html", page_documents(rendered_docs, data))
    write(out / "requirements.html", page_requirements(data))
    write(out / "review.html", page_review(data))
    write(out / "404.html", page_not_found(data))

    for topic_data in data.get("topics", []):
        slug = topic_slug(topic_data["topic"])
        write(topics_dir / f"{slug}.html", page_topic(topic_data, data, depth=1))
        if write_data:
            data_dir.mkdir(parents=True, exist_ok=True)
            (data_dir / "topics").mkdir(parents=True, exist_ok=True)
            (data_dir / "topics" / f"{slug}.json").write_text(
                json.dumps(topic_data, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8"
            )
            written.append(data_dir / "topics" / f"{slug}.json")

    if write_data:
        for name, payload in (
            ("index.json", data),
            ("sources.json", data.get("sources", {})),
            ("irregularities.json", data.get("irregularities", [])),
            ("requirements.json", data.get("requirements", [])),
            ("methodology.json", data.get("methodology", {})),
            ("experiments.json", data.get("experiments", [])),
            ("meta.json", {"generated_at": data.get("generated_at"), "run_id": data.get("run_id"), "counts": data.get("counts", {}), "checks": data.get("checks", {})}),
        ):
            path = data_dir / name
            path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
            written.append(path)

    return written
