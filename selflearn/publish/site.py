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


def confidence_badge(confidence: str) -> str:
    kind = {"high": "ok", "medium": "info", "low": "warn", "unknown": ""}.get(confidence, "")
    return badge(confidence, kind)


def pct(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:.1f}%"


def layout(title: str, body: str, *, active: str, data: dict[str, Any], depth: int = 0) -> str:
    prefix = "../" * depth
    # A rebuild from stored data must not read as a fresh retrieval.
    rebuilt = data.get("rebuilt_at")
    rebuild_note = f" &middot; rebuilt from the stored library at {esc(rebuilt)}" if rebuilt else ""
    nav_parts = []
    for href, label in NAV:
        current = ' aria-current="page"' if href == active else ""
        nav_parts.append(f'<a href="{prefix}{href}"{current}>{esc(label)}</a>')
    nav_items = "".join(nav_parts)
    mode = data.get("mode", "unknown")
    generated = data.get("generated_at", utcnow_iso())
    mode_banner = ""
    if mode == "fixture":
        mode_banner = (
            '<div class="banner err wrap"><strong>Test run.</strong> This site was generated in fixture mode, which '
            "exists to test the pipeline: any fixture evidence in it is synthetic and is labelled as such on every "
            "claim. Nothing here is presented as a real-world finding. Run the engine in live or snapshot mode before "
            "reading anything on these pages as research.</div>"
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
      <span class="muted small">run <span class="mono">{esc(data.get('run_id') or 'n/a')}</span> &middot; generated {esc(generated)} &middot; mode {esc(mode)}{rebuild_note}</span>
    </div>
    <nav class="site" aria-label="Primary">{nav_items}</nav>
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


def table(headers: Iterable[str], rows: Iterable[Iterable[str]], *, caption: str = "", sortable: bool = False, scroll: bool = True) -> str:
    head = "".join(f"<th scope=\"col\">{esc(h)}</th>" for h in headers)
    body_rows = []
    for row in rows:
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
    leaderboard = (data.get("elo") or {}).get("leaderboard", [])
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

{section("Competition standings", (
    table(["#", "Brief", "Rating", "Wins / matches"], leaderboard_rows,
          caption="Elo ratings over head-to-head tournament results. Ratings accumulate across cycles and questions.")
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
        detail = (
            f"<blockquote>{esc(quote)}<cite>{esc(claim['source_name'])} &middot; {link(claim.get('url'), 'source')} "
            f"&middot; snapshot <span class='mono'>{esc(claim.get('evidence_id'))}</span></cite></blockquote>"
            f"<p class='small'>Coverage {esc(pct(claim.get('coverage')))} &middot; verbatim quote match: "
            f"{'yes' if claim.get('quote_match') else 'no'} &middot; recorded {esc(claim.get('recorded_at'))}</p>"
            f"{missing}<ul class='small'>{reasons}</ul>"
        )
        fact_rows.append(
            [
                f'<div id="claim-{esc(claim["claim_id"])}" class="anchor">{esc(claim.get("text", ""))}</div>'
                + details("Show the quoted span and how it was checked", detail),
                esc(claim.get("source_name", "")),
                class_badge(int(claim.get("evidence_rank", 9)), claim.get("evidence_class_label", "")),
                verdict_badge(claim.get("verdict", "")),
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

{section("Verified facts", (table(["Statement", "Source", "Evidence class", "Verification", "Confidence", "Link"], fact_rows, sortable=True)
        if fact_rows else "<p>No claims have been recorded for this question yet.</p>"),
        anchor="facts",
        note="A statement is listed here only if it passed the verification check described on the method page. Claims that "
             "failed stay in the library and appear on the review page.")}

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
                    {"reachable": "reached", "unreachable": "unreachable", "error": "error", "credential_required": "needs key", "not_attempted": "not tried"}.get(live_status, live_status),
                    {"reachable": "ok", "unreachable": "err", "error": "err", "credential_required": "warn"}.get(live_status, ""),
                ),
                ("needs " + str(spec.get("key_env")) if spec.get("requires_key") else "open"),
                link(spec.get("docs_url"), "docs"),
                f'<span class="num">{rel_row.get("documents", 0)}</span>',
                f'<span class="num">{rel_row.get("claims_proposed", 0)}</span>',
                f'<span class="num">{pct(rel_row.get("support_rate")) if rel_row.get("claims_proposed") else "&mdash;"}</span>',
                esc(health.get("detail", "") or spec.get("rate_limit_note", ""))[:220],
            ]
        )

    counts = {
        "total": len(matrix),
        "reached": sum(1 for row in status.values() if row.get("live_status") == "reachable"),
        "unreachable": sum(1 for row in status.values() if row.get("live_status") in {"unreachable", "error"}),
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

{section("What to do about a source that fails", bullet_list([
    "Unreachable sources are reported on the review page with the transport error, so the gap is visible.",
    "A source that repeatedly returns HTTP errors is a candidate for a fix in the adapter, not for silent removal.",
    "Credentials are read from environment variables named in the table. The engine never stores a credential in the repository.",
]), anchor="failures")}
"""
    return layout("Sources", body, active="sources.html", data=data, depth=depth)


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

    irregularity_rows = [
        [
            badge(item.get("severity", ""), {"error": "err", "warning": "warn"}.get(item.get("severity", ""), "info")),
            esc(item.get("stage", "")),
            esc(item.get("summary", "")),
            esc(item.get("detail", ""))[:400],
            link(item.get("url"), "link") if item.get("url") else "&mdash;",
            esc(item.get("suggested_action", "")),
            esc(item.get("created_at", "")),
        ]
        for item in sorted(irregularities, key=lambda row: ({"error": 0, "warning": 1, "info": 2}.get(row.get("severity", "info"), 3), row.get("stage", "")))
    ]
    failure_rows = [
        [esc(item.get("stage", "")), esc(item.get("summary", "")), esc(item.get("detail", ""))[:300], esc(item.get("remedy", ""))]
        for item in failures
    ]
    contradiction_rows = [
        [esc(item.get("topic_id", "")), esc(item.get("kind", "")), esc(item.get("detail", "")), esc(item.get("claim_a", "")) + " / " + esc(item.get("claim_b", ""))]
        for item in contradictions
    ]
    disagreements = calibration.get("disagreements") or []
    disagreement_rows = [[esc(d.get("case_id")), esc(d.get("name")), esc(d.get("expected")), esc(d.get("predicted"))] for d in disagreements]

    body = f"""
<h1>For review</h1>
<p class="lede">This page is the point of the project: everything the engine could not reconcile on its own. Each entry
says what was found, where, and what would resolve it. Nothing here is a conclusion.</p>
<div class="grid four">
{stat(checks.get('irregularity_counts', {}).get('error', 0), 'errors')}
{stat(checks.get('irregularity_counts', {}).get('warning', 0), 'warnings')}
{stat(checks.get('unresolved_contradictions', 0), 'unresolved contradictions')}
{stat(len(failures), 'recorded failures')}
</div>
<div class="banner info"><strong>How to act on this page.</strong> An entry is either a genuine problem in the engine
(a source that moved, a parser that broke, a threshold that is wrong) or a genuine problem in the evidence (sources
disagree, or a claim cannot be checked). The suggested action states which. Reproduce the whole audit with
<span class="mono">python -m selflearn audit</span> and read the machine-readable list in
<span class="mono">docs/data/irregularities.json</span>.</div>

{section("Irregularities", table(
    ["Severity", "Stage", "Finding", "Detail", "Link", "Suggested action", "Detected"], irregularity_rows, sortable=True)
    if irregularity_rows else "<p>No irregularities were detected in this run.</p>", anchor="irregularities")}

{section("Label disagreements", table(
    ["Case", "Name", "Human label", "Engine verdict"], disagreement_rows) if disagreement_rows else
    "<p>The verifier agrees with every human label in the calibration set, except the cases documented as engine "
    "limitations, which are listed on the method page.</p>", anchor="labels",
    note="These are the cases where the engine's verdict differs from a hand-written label. They are the most informative rows on this page.")}

{section("Candidate contradictions", table(
    ["Question", "Kind", "Why it was flagged", "Claims"], contradiction_rows) if contradiction_rows else
    "<p>No candidate contradictions are open.</p>", anchor="contradictions")}

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


def page_root_entry(data: dict[str, Any]) -> str:
    """The repository-root landing page that GitHub Pages serves.

    GitHub Pages publishes this repository from the branch root, while the engine
    writes the site into ``docs/``. Rather than move the site, this single page is
    written next to it: a reader arriving at the Pages URL gets one clear entry
    point, and every link on it is relative so it works from any host.
    """
    counts = data.get("counts") or {}
    topics = data.get("topics") or []
    run_id = data.get("run_id") or "no run recorded"
    mode = data.get("mode") or "unknown"
    generated = data.get("generated_at") or ""
    topic_items = "".join(
        f'<li>{rel(topic_href(item["topic"], prefix="docs/"), item["topic"].get("title", "question"))} '
        f'<span class="muted">- {esc((item.get("topic") or {}).get("status", ""))}</span></li>'
        for item in topics[:6]
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SelfLearn - autonomous evidence-verifying research engine</title>
<meta name="description" content="SelfLearn researches questions from public sources and publishes only what it can quote from a retrieved document.">
<meta name="color-scheme" content="light dark">
<style>
:root {{ --ink:#10202c; --muted:#5b6b78; --line:#c9d3da; --bg:#f7f9fb; --card:#fff; --accent:#0b5d7a; }}
@media (prefers-color-scheme: dark) {{ :root {{ --ink:#e8eef2; --muted:#9fb0bd; --line:#2b3a45; --bg:#121a20; --card:#18232b; --accent:#7cc4de; }} }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--ink); font:16px/1.6 system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif; }}
main {{ max-width:44rem; margin:0 auto; padding:3rem 1.25rem 4rem; }}
h1 {{ font-size:1.9rem; margin:0 0 .25rem; }}
h2 {{ font-size:1.15rem; margin:2rem 0 .5rem; }}
p {{ margin:.6rem 0; }}
.lede {{ font-size:1.05rem; }}
.muted {{ color:var(--muted); }}
.card {{ background:var(--card); border:1px solid var(--line); border-radius:10px; padding:1rem 1.25rem; margin:1.25rem 0; }}
a {{ color:var(--accent); }}
ul {{ padding-left:1.2rem; }}
.cta {{ display:inline-block; background:var(--accent); color:#fff; padding:.6rem 1rem; border-radius:8px; text-decoration:none; font-weight:600; }}
@media (prefers-color-scheme: dark) {{ .cta {{ color:#08131a; }} }}
code {{ font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; }}
.small {{ font-size:.9rem; }}
</style>
</head>
<body>
<main>
  <h1>SelfLearn</h1>
  <p class="lede">An autonomous research engine that will not publish a sentence it cannot quote from a
  document it actually retrieved. No language model is used at any stage: every claim is a span of a
  stored source, and the accept/reject decision is a string comparison a reviewer can re-run.</p>

  <p><a class="cta" href="docs/index.html">Open the research site &rarr;</a></p>
  <p class="muted small">Last published run <code>{esc(run_id)}</code> ({esc(mode)} mode), generated {esc(generated)}:
  {esc(counts.get("topics", 0))} questions, {esc(counts.get("claims", 0))} claims over
  {esc(counts.get("documents", 0))} stored documents.</p>

  <div class="card">
    <h2 style="margin-top:0">Go straight to</h2>
    <ul>
      <li>{rel("docs/index.html", "Overview")} - what the engine is doing and what changed this cycle</li>
      <li>{rel("docs/review.html", "For review")} - every unresolved irregularity, failure and contradiction</li>
      <li>{rel("docs/sources.html", "Sources")} - what was read, what was reachable, what needs a credential</li>
      <li>{rel("docs/method.html", "Method")} - evidence hierarchy, thresholds in force, criteria, refusals</li>
      <li>{rel("docs/documents.html", "Documents")} - design source, architecture, verification, limits, roadmap</li>
      <li>{rel("docs/requirements.html", "Requirements")} - the brief traced line by line</li>
    </ul>
    {f'<p class="muted">Questions currently under research:</p><ul>{topic_items}</ul>' if topic_items else ''}
  </div>

  <h2>Check it yourself</h2>
  <p>Every figure on the site is traceable to a claim or to a count the engine recorded. The stored
  bytes behind each claim, the calibration that set the verification thresholds, the experiment results
  and the run summary are all committed to the repository.</p>
  <ul class="muted">
    <li><code>python3 tools/check_claim.py</code> - a claim, its document, its hash, a fresh re-check</li>
    <li><code>python3 -m selflearn audit</code> - re-verify every claim from its snapshot</li>
    <li><code>python3 -m selflearn selftest</code> - the test suite</li>
  </ul>
  <p class="muted small">Source code: {link(ENGINE_REPO_URL, "github.com/buffedlizard55-lab/SelfLearn")}.
  No third-party scripts, fonts or trackers.</p>
</main>
</body>
</html>
"""


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
        (root / ".nojekyll").write_text("", encoding="utf-8")
        written.extend([root / "index.html", root / ".nojekyll"])
    write(out / "index.html", page_index(data))
    write(out / "library.html", page_library(data))
    write(out / "sources.html", page_sources(data))
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
