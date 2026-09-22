"""Static assets for the published site: one stylesheet, one small script.

Both are written from source so the site has no build step and no third-party
requests. A reader can audit the entire front end by reading this file.
"""

from __future__ import annotations

STYLESHEET = """\
/* SelfLearn published site - hand-written CSS, no framework, no external fonts. */
:root {
  --bg: #f7f8fa;
  --surface: #ffffff;
  --surface-2: #f1f3f7;
  --text: #16202c;
  --muted: #5b6878;
  --border: #dde2ea;
  --accent: #1d5fd4;
  --accent-soft: #e6eefc;
  --ok: #15653f;
  --ok-soft: #e2f3e9;
  --warn: #7a5200;
  --warn-soft: #fdf1d9;
  --err: #98231f;
  --err-soft: #fbe6e5;
  --info: #2a4b7c;
  --info-soft: #e7eefb;
  --radius: 10px;
  --mono: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
  --sans: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #0f141a;
    --surface: #161d26;
    --surface-2: #1d2631;
    --text: #e7edf5;
    --muted: #9aa8b8;
    --border: #2a3746;
    --accent: #77a8ff;
    --accent-soft: #1b2b47;
    --ok: #7fdcab;
    --ok-soft: #172c22;
    --warn: #f2c66d;
    --warn-soft: #33280f;
    --err: #ff9c98;
    --err-soft: #3a1e1d;
    --info: #a6c3f5;
    --info-soft: #17263c;
  }
}
/* An explicit choice beats the media query, so the toggle below has something to
   change. Both blocks repeat the full set: a half-applied theme is worse than
   none, because a stray light surface on a dark page is unreadable. */
[data-theme="light"] {
    --bg: #f7f8fa;
    --surface: #ffffff;
    --surface-2: #f1f3f7;
    --text: #16202c;
    --muted: #5b6878;
    --border: #dde2ea;
    --accent: #1d5fd4;
    --accent-soft: #e6eefc;
    --ok: #15653f;
    --ok-soft: #e2f3e9;
    --warn: #7a5200;
    --warn-soft: #fdf1d9;
    --err: #98231f;
    --err-soft: #fbe6e5;
    --info: #2a4b7c;
    --info-soft: #e7eefb;
}
[data-theme="dark"] {
    --bg: #0f141a;
    --surface: #161d26;
    --surface-2: #1d2631;
    --text: #e7edf5;
    --muted: #9aa8b8;
    --border: #2a3746;
    --accent: #77a8ff;
    --accent-soft: #1b2b47;
    --ok: #7fdcab;
    --ok-soft: #172c22;
    --warn: #f2c66d;
    --warn-soft: #33280f;
    --err: #ff9c98;
    --err-soft: #3a1e1d;
    --info: #a6c3f5;
    --info-soft: #17263c;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: var(--sans);
  line-height: 1.6;
  font-size: 16px;
  -webkit-text-size-adjust: 100%;
}
a { color: var(--accent); text-decoration-thickness: 1px; text-underline-offset: 2px; }
a:hover { text-decoration-thickness: 2px; }
:focus-visible { outline: 3px solid var(--accent); outline-offset: 2px; border-radius: 4px; }
.cta {
  display: inline-block; background: var(--accent); color: #fff; padding: .55rem 1rem;
  border-radius: 8px; text-decoration: none; font-weight: 600; border: 1px solid var(--accent);
}
.cta:hover { text-decoration: none; filter: brightness(1.08); }
[data-theme="dark"] .cta, :root .cta { color: #fff; }
@media (prefers-color-scheme: dark) { .cta { color: #08131a; } }
[data-theme="dark"] .cta { color: #08131a; }
[data-theme="light"] .cta { color: #fff; }
.icon-btn {
  background: var(--surface); color: var(--muted); border: 1px solid var(--border);
  border-radius: 999px; padding: .25rem .7rem; font: inherit; font-size: .82rem; cursor: pointer;
}
.icon-btn:hover { color: var(--text); background: var(--surface-2); }
.skip { position: absolute; left: -9999px; }
.skip:focus { left: 1rem; top: 1rem; background: var(--surface); padding: .5rem .75rem; border-radius: 6px; z-index: 50; }

header.site {
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  position: sticky; top: 0; z-index: 20;
}
.wrap { max-width: 1120px; margin: 0 auto; padding: 0 1.1rem; }
header.site .bar { display: flex; flex-wrap: wrap; gap: .35rem 1rem; align-items: baseline; padding: .8rem 0 .55rem; }
.brand { font-weight: 700; font-size: 1.05rem; letter-spacing: -.01em; }
.brand small { font-weight: 500; color: var(--muted); font-size: .8rem; margin-left: .45rem; }
nav.site { display: flex; flex-wrap: wrap; gap: .25rem; padding-bottom: .65rem; align-items: center; }
nav.site .spacer { flex: 1 1 auto; }
nav.site a {
  padding: .3rem .6rem; border-radius: 999px; text-decoration: none; color: var(--muted);
  border: 1px solid transparent; font-size: .93rem;
}
nav.site a:hover { background: var(--surface-2); color: var(--text); }
nav.site a[aria-current="page"] { background: var(--accent-soft); color: var(--accent); border-color: var(--border); font-weight: 600; }

main { padding: 1.6rem 0 3rem; }
h1 { font-size: 1.7rem; line-height: 1.25; margin: .2rem 0 .6rem; letter-spacing: -.02em; }
h2 { font-size: 1.25rem; margin: 2rem 0 .6rem; letter-spacing: -.01em; }
h3 { font-size: 1.02rem; margin: 1.3rem 0 .5rem; }
p, li { max-width: 78ch; }
.lede { font-size: 1.06rem; color: var(--muted); max-width: 80ch; }
.muted { color: var(--muted); }
.small { font-size: .86rem; }
.mono { font-family: var(--mono); font-size: .86em; word-break: break-word; }
hr { border: 0; border-top: 1px solid var(--border); margin: 2rem 0; }

.banner { border-radius: var(--radius); padding: .8rem 1rem; margin: 1rem 0; border: 1px solid var(--border); background: var(--surface); }
.banner.warn { background: var(--warn-soft); border-color: var(--warn); color: var(--warn); }
.banner.err { background: var(--err-soft); border-color: var(--err); color: var(--err); }
.banner.info { background: var(--info-soft); border-color: var(--info); color: var(--info); }
.banner strong { color: inherit; }

.grid { display: grid; gap: 1rem; }
.grid.two { grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); }
.grid.three { grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); }
.grid.four { grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); }

.card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 1rem 1.1rem; }
.card h3:first-child, .card h2:first-child { margin-top: 0; }
.card .sub { color: var(--muted); font-size: .88rem; }
.stat { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: .85rem 1rem; }
.stat .n { display: block; font-size: 1.7rem; font-weight: 700; line-height: 1.1; }
.stat .l { color: var(--muted); font-size: .85rem; }

table { width: 100%; border-collapse: collapse; margin: .7rem 0 1rem; font-size: .93rem; background: var(--surface); }
caption { text-align: left; color: var(--muted); font-size: .86rem; padding: .3rem 0; }
th, td { text-align: left; vertical-align: top; padding: .5rem .55rem; border-bottom: 1px solid var(--border); }
thead th { background: var(--surface-2); position: sticky; top: 0; font-size: .86rem; text-transform: uppercase; letter-spacing: .04em; color: var(--muted); }
tbody tr:nth-child(even) { background: color-mix(in srgb, var(--surface-2) 45%, transparent); }
td.num { font-variant-numeric: tabular-nums; text-align: right; }
.table-scroll { overflow-x: auto; }

.badge { display: inline-block; padding: .1rem .5rem; border-radius: 999px; font-size: .78rem; font-weight: 600; border: 1px solid var(--border); background: var(--surface-2); color: var(--muted); white-space: nowrap; }
.badge.ok { background: var(--ok-soft); color: var(--ok); border-color: var(--ok); }
.badge.warn { background: var(--warn-soft); color: var(--warn); border-color: var(--warn); }
.badge.err { background: var(--err-soft); color: var(--err); border-color: var(--err); }
.badge.info { background: var(--info-soft); color: var(--info); border-color: var(--info); }
.badge.rank1 { background: var(--ok-soft); color: var(--ok); border-color: var(--ok); }
.badge.rank2 { background: var(--info-soft); color: var(--info); border-color: var(--info); }
.badge.rank3 { background: var(--warn-soft); color: var(--warn); border-color: var(--warn); }

blockquote { margin: .5rem 0; padding: .55rem .8rem; border-left: 3px solid var(--accent); background: var(--surface-2); border-radius: 0 6px 6px 0; }
blockquote cite { display: block; color: var(--muted); font-size: .85rem; font-style: normal; margin-top: .3rem; }
details { border: 1px solid var(--border); border-radius: 8px; padding: .5rem .7rem; margin: .5rem 0; background: var(--surface); }
details summary { cursor: pointer; font-weight: 600; }
details[open] summary { margin-bottom: .5rem; }
pre { background: var(--surface-2); border: 1px solid var(--border); border-radius: 8px; padding: .7rem .8rem; overflow-x: auto; font-family: var(--mono); font-size: .86rem; }
code { font-family: var(--mono); font-size: .88em; background: var(--surface-2); padding: .05rem .3rem; border-radius: 4px; }
pre code { background: none; padding: 0; }

.bar-meter { height: 8px; border-radius: 999px; background: var(--surface-2); overflow: hidden; border: 1px solid var(--border); }
.bar-meter span { display: block; height: 100%; background: var(--accent); }

.filter { display: flex; gap: .5rem; flex-wrap: wrap; align-items: center; margin: .8rem 0; }
.filter input, .filter select { padding: .45rem .6rem; border-radius: 8px; border: 1px solid var(--border); background: var(--surface); color: var(--text); font: inherit; }
.timeline { display: flex; flex-wrap: wrap; gap: .3rem; list-style: none; padding: 0; margin: .4rem 0; }
.timeline li { font-size: .8rem; padding: .1rem .5rem; border-radius: 999px; border: 1px dashed var(--border); color: var(--muted); }
.timeline li.done { border-style: solid; border-color: var(--ok); color: var(--ok); background: var(--ok-soft); }

footer.site { border-top: 1px solid var(--border); background: var(--surface); padding: 1.4rem 0 2.4rem; color: var(--muted); font-size: .9rem; }
footer.site a { color: var(--accent); }
.toc { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: .8rem 1rem; }
.toc ul { margin: .3rem 0 0; padding-left: 1.1rem; }
.winner { border-left: 4px solid var(--ok); }
.unknown { border-left: 4px solid var(--warn); }
.anchor { scroll-margin-top: 6rem; }

@media print {
  header.site, nav.site, .filter, footer.site { display: none; }
  body { background: white; color: black; }
  details { border: 0; }
  details[open] summary, details summary { list-style: none; }
}
"""

SCRIPT = """\
/* SelfLearn site script: client-side filtering only. No network calls, no trackers. */
(function () {
  "use strict";

  function normalise(value) {
    return (value || "").toString().toLowerCase();
  }

  document.querySelectorAll("[data-filter-target]").forEach(function (input) {
    var target = document.querySelector(input.getAttribute("data-filter-target"));
    if (!target) return;
    var rows = Array.prototype.slice.call(target.querySelectorAll("[data-row]"));
    var count = document.querySelector(input.getAttribute("data-count-target"));
    function apply() {
      var needle = normalise(input.value);
      var select = input.getAttribute("data-filter-select");
      var chosen = select ? normalise((document.querySelector(select) || {}).value) : "";
      var visible = 0;
      rows.forEach(function (row) {
        var haystack = normalise(row.getAttribute("data-search") || row.textContent);
        var kind = normalise(row.getAttribute("data-kind"));
        var match = (!needle || haystack.indexOf(needle) !== -1) && (!chosen || kind === chosen);
        row.hidden = !match;
        if (match) visible += 1;
      });
      if (count) count.textContent = visible + " of " + rows.length + " shown";
    }
    input.addEventListener("input", apply);
    var select = input.getAttribute("data-filter-select");
    if (select) {
      var el = document.querySelector(select);
      if (el) el.addEventListener("change", apply);
    }
    apply();
  });

  document.querySelectorAll("table[data-sortable]").forEach(function (table) {
    table.querySelectorAll("thead th").forEach(function (th, index) {
      th.style.cursor = "pointer";
      th.title = "Sort by this column";
      th.addEventListener("click", function () {
        var body = table.tBodies[0];
        var rows = Array.prototype.slice.call(body.rows);
        var ascending = th.getAttribute("data-sort-dir") !== "asc";
        rows.sort(function (a, b) {
          var left = a.cells[index] ? a.cells[index].innerText.trim() : "";
          var right = b.cells[index] ? b.cells[index].innerText.trim() : "";
          var leftNum = parseFloat(left.replace(/[,%]/g, ""));
          var rightNum = parseFloat(right.replace(/[,%]/g, ""));
          var numeric = !isNaN(leftNum) && !isNaN(rightNum);
          var result = numeric ? leftNum - rightNum : left.localeCompare(right);
          return ascending ? result : -result;
        });
        rows.forEach(function (row) { body.appendChild(row); });
        th.setAttribute("data-sort-dir", ascending ? "asc" : "desc");
      });
    });
  });

  document.querySelectorAll("[data-copy]").forEach(function (button) {
    button.addEventListener("click", function () {
      var text = button.getAttribute("data-copy");
      if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(function () {
          button.textContent = "Copied";
          setTimeout(function () { button.textContent = "Copy"; }, 1500);
        });
      }
    });
  });

  var toggle = document.querySelector("[data-theme-toggle]");
  if (toggle) {
    /* Resolving "no explicit theme yet" against the media query is what makes the
       first click do what the reader expects rather than what the attribute says. */
    function current() {
      var set = document.documentElement.getAttribute("data-theme");
      if (set) return set;
      return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    }
    function sync() {
      toggle.setAttribute("aria-pressed", current() === "dark" ? "true" : "false");
      toggle.textContent = current() === "dark" ? "Light theme" : "Dark theme";
    }
    toggle.addEventListener("click", function () {
      var next = current() === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", next);
      try { localStorage.setItem("selflearn-theme", next); } catch (e) {}
      sync();
    });
    sync();
  }
})();
"""
