"""A tiny, dependency-free Markdown renderer for the hand-written documents.

The project has no third-party dependencies (see ``pyproject.toml``), so the
repository documents under ``docs/*.md`` cannot be rendered by an external
library. This module implements the small subset of Markdown those documents
actually use - headings, paragraphs, lists, fenced code, blockquotes, pipe
tables, rules and inline emphasis/code/links - and nothing else.

Two properties matter more than coverage:

* **Everything is escaped first.** Text is HTML-escaped before any markup is
  inserted, so a document can never inject script into the site.
* **Only safe link schemes survive.** A link whose target is not ``http``,
  ``https``, ``mailto`` or a relative path is rendered as plain text.
"""

from __future__ import annotations

import html
import re

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
FENCE_RE = re.compile(r"^```(.*)$")
RULE_RE = re.compile(r"^\s*([-*_])(\s*\1){2,}\s*$")
ULIST_RE = re.compile(r"^\s*[-*+]\s+(.*)$")
OLIST_RE = re.compile(r"^\s*\d+[.)]\s+(.*)$")
QUOTE_RE = re.compile(r"^\s*>\s?(.*)$")
TABLE_SEP_RE = re.compile(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)+\|?\s*$")
SAFE_SCHEME_RE = re.compile(r"^(https?:|mailto:|#|\.{0,2}/)", re.IGNORECASE)

INLINE_CODE_RE = re.compile(r"`([^`]+)`")
BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")
ITALIC_RE = re.compile(r"(?<!\*)\*([^*]+)\*(?!\*)")
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
AUTOLINK_RE = re.compile(r"(?<![\"'>=])\bhttps?://[^\s<>()\"']+")


def _slug(text: str) -> str:
    """GitHub-compatible heading anchor: lowercase, alphanumerics and dashes."""
    lowered = text.strip().casefold()
    lowered = re.sub(r"[^\w\s-]", "", lowered)
    return re.sub(r"[\s_]+", "-", lowered).strip("-") or "section"


def _safe_href(target: str) -> str:
    target = target.strip()
    if SAFE_SCHEME_RE.match(target):
        return target
    return ""


def inline(text: str) -> str:
    """Render inline Markdown, escaping everything that is not markup."""
    out = html.escape(text, quote=False)
    out = INLINE_CODE_RE.sub(lambda m: f"<code>{m.group(1)}</code>", out)
    out = LINK_RE.sub(lambda m: _link(m.group(1), m.group(2)), out)
    out = BOLD_RE.sub(lambda m: f"<strong>{m.group(1)}</strong>", out)
    out = ITALIC_RE.sub(lambda m: f"<em>{m.group(1)}</em>", out)
    out = AUTOLINK_RE.sub(lambda m: _autolink(m.group(0)), out)
    return out


def _link(label: str, target: str) -> str:
    href = _safe_href(html.unescape(target))
    if not href:
        return f"{label} (link stripped: unsupported scheme {html.escape(target)})"
    external = ' target="_blank" rel="noopener noreferrer"' if href.startswith(("http", "mailto")) else ""
    return f'<a href="{html.escape(href, quote=True)}"{external}>{label}</a>'


def _autolink(url: str) -> str:
    href = html.unescape(url).rstrip(".,;:")
    tail = url[len(href) :]
    return f'<a href="{html.escape(href, quote=True)}" target="_blank" rel="noopener noreferrer">{href}</a>{tail}'


def _table(rows: list[str]) -> str:
    def cells(row: str) -> list[str]:
        stripped = row.strip().strip("|")
        return [inline(cell.strip()) for cell in stripped.split("|")]

    header = cells(rows[0])
    body = [cells(row) for row in rows[2:]]
    head_html = "".join(f"<th scope=\"col\">{c}</th>" for c in header)
    body_html = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in body)
    return f'<div class="table-scroll"><table><thead><tr>{head_html}</tr></thead><tbody>{body_html}</tbody></table></div>'


def render(text: str) -> tuple[str, list[tuple[int, str, str]]]:
    """Render Markdown to HTML.

    Returns ``(html, headings)`` where each heading is ``(level, anchor, title)``
    so the caller can build a table of contents without re-parsing.
    """
    lines = text.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    headings: list[tuple[int, str, str]] = []
    paragraph: list[str] = []
    list_items: list[str] = []
    list_tag = ""
    quote: list[str] = []
    table_rows: list[str] = []
    code: list[str] = []
    in_code = False

    def flush_paragraph() -> None:
        if paragraph:
            out.append(f"<p>{inline(' '.join(paragraph).strip())}</p>")
            paragraph.clear()

    def flush_list() -> None:
        nonlocal list_tag
        if list_items:
            out.append(f"<{list_tag}>" + "".join(f"<li>{item}</li>" for item in list_items) + f"</{list_tag}>")
            list_items.clear()
            list_tag = ""

    def flush_quote() -> None:
        if quote:
            out.append("<blockquote>" + " ".join(f"<p>{inline(q)}</p>" for q in quote) + "</blockquote>")
            quote.clear()

    def flush_table() -> None:
        if not table_rows:
            return
        if len(table_rows) >= 2:
            out.append(_table(table_rows))
        else:
            # A lone pipe line is not a table; render it as a paragraph.
            out.append(f"<p>{inline(table_rows[0].strip())}</p>")
        table_rows.clear()

    def flush_all() -> None:
        flush_paragraph()
        flush_list()
        flush_quote()
        flush_table()

    for line in lines:
        fence = FENCE_RE.match(line)
        if in_code:
            if fence:
                out.append("<pre><code>" + html.escape("\n".join(code)) + "</code></pre>")
                code.clear()
                in_code = False
            else:
                code.append(line)
            continue
        if fence:
            flush_all()
            in_code = True
            continue

        if not line.strip():
            flush_all()
            continue
        if RULE_RE.match(line):
            flush_all()
            out.append("<hr>")
            continue
        heading = HEADING_RE.match(line)
        if heading:
            flush_all()
            level = len(heading.group(1))
            title = heading.group(2).strip()
            anchor = _slug(title)
            headings.append((level, anchor, title))
            out.append(f'<h{level} id="{html.escape(anchor, quote=True)}">{inline(title)}</h{level}>')
            continue
        if TABLE_SEP_RE.match(line) and table_rows:
            table_rows.append(line)
            continue
        if line.lstrip().startswith("|"):
            # Pipe rows are buffered; flush_table() decides whether a separator
            # row arrived, which is what makes it a table rather than prose.
            flush_paragraph()
            table_rows.append(line)
            continue
        if table_rows:
            flush_table()
        ordered = OLIST_RE.match(line)
        bullet = ULIST_RE.match(line)
        if ordered or bullet:
            flush_paragraph()
            flush_quote()
            tag = "ol" if ordered else "ul"
            if list_tag and list_tag != tag:
                flush_list()
            list_tag = tag
            list_items.append(inline((ordered or bullet).group(1).strip()))
            continue
        quoted = QUOTE_RE.match(line)
        if quoted:
            flush_paragraph()
            flush_list()
            quote.append(quoted.group(1).strip())
            continue
        flush_list()
        flush_quote()
        paragraph.append(line.strip())

    if in_code and code:  # unterminated fence: render what we have rather than lose it
        out.append("<pre><code>" + html.escape("\n".join(code)) + "</code></pre>")
    flush_all()
    return "\n".join(out), headings
