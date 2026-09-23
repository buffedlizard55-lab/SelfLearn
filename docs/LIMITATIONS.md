# Limitations

Everything below is a way this engine falls short of the design document, of the
brief, or of what a reader might reasonably assume. None of it is hidden anywhere in
the published output: the same list appears on the site's method page and, where a
limit affects a specific statement, the statement itself carries the warning.

## What the engine cannot do at all

1. **It cannot reason beyond its rules.** There is no language model in the pipeline.
   Claims are spans cut from documents; candidates are quotations plus fixed
   scaffolding; critics are eleven named rules; the tournament is arithmetic. The
   engine never paraphrases and never synthesises an explanation. A question whose
   answer is not already a sentence in a retrieved document cannot be answered.
2. **It cannot run a physical experiment.** The experiment catalogue is computational:
   threshold calibration, sorting and search comparison counts, hash collision rates,
   scheduling policies on a synthetic bandit, estimation error on synthetic
   populations, and queueing formulas checked against simulation. Statements about the
   world can be sourced, quoted and contradicted, but not tested here.
3. **It cannot decide which of two contradicting sources is right.** Contradictions
   are detected and published as review items; the resolution is a human step.
4. **It cannot read behind paywalls, logins or licences that forbid retrieval.** Only
   open APIs and open documents are used.
5. **It cannot read a chart, an image or a PDF it cannot fetch as text.** Documents
   are text; a figure's numbers are not extracted from the picture.

## What it does, but weakly

6. **Verification is lexical, not semantic.** Fabricated numbers, missing dates,
   polarity flips and direction reversals are caught. Unit substitution is not: a
   claim saying "50 dollars" against a document saying "50 euros" passes the number
   check and the token check. That case is labelled `c23` in
   `data/fixtures/verification_cases.jsonl` and is excluded from threshold
   calibration, visibly, with a reason recorded on the case itself.
7. **Paraphrase detection is a token heuristic.** A faithful paraphrase in different
   words scores low and is downgraded to "needs review"; a misleading paraphrase in
   the source's own words scores high.
8. **Attention is not importance.** Repository stars, forum threads and comment counts
   are used only to prioritise what to read next. They are commentary-class signals
   and are never evidence that something is true.
9. **Freshness depends on the source.** The engine records what each source returned
   and when, but it cannot make a source revise itself. A stale official series is
   quoted as the current published value, with its own date attached.
10. **Entity resolution is textual.** Two names for the same thing are two things
    unless the source links them.
11. **The relevance filter is lexical.** A result that shares no meaningful token with
    the query is dropped, and the number dropped is reported. A relevant document
    phrased in unseen vocabulary can be dropped too.
12. **The site is a rebuild, not an app.** Every page is static HTML generated from
    the stored data. Filtering and sorting happen in the browser with a small script;
    nothing is queried live and there is no server.

## Limits of the layers added on 2026-09-21

13. **The substance score is lexical.** It counts numbers, dates, comparatives, causal
    phrases and word length, and weights them by a published constant. A claim written in
    dense prose without a digit scores as metadata even when it carries a finding, and a
    claim that merely recites a number scores as substantive. It orders reading and labels
    metadata; it never overrides a verification verdict, and it is not a measure of truth.
14. **Synthesis matches units by word.** A range or a divergence statement is built when
    two documents carry different figures followed by the same word. Two sources using one
    word for two different measures would be combined, which is why those statements are
    published as needing review and why the engine never averages: the arithmetic that
    would produce an average is not performed anywhere in the pipeline.
15. **Change scanning covers five sources.** Crossref, arXiv, GitHub, NVD and USGS
    document a change filter; the other registered sources do not, and are reported as
    having none rather than polled. An item published in a window the engine could not
    reach is not missed - it appears as new on a later run - but the window it is
    attributed to will be wrong.
16. **The USPTO adapter has never met a real response.** The request and response shapes
    are the operator's documented ones and are covered by tests against the published
    sample, but no key is configured, so no live call has been made. The first real
    response may differ from the documentation, and the adapter's fallback is to store the
    response verbatim rather than guess.
17. **Topic invention can propose a topic that is not interesting.** The gates are
    arithmetic thresholds over counts. A phrase can clear them because two documents
    happen to share it. Every proposal is published with its components and the reason it
    was accepted or rejected, and a reviewer can close one with
    `tools/reject_topic.py` without destroying the record.

## Operational limits

18. **A cycle is a process, not a daemon.** Continuity comes from the schedule that
    starts it: `.github/workflows/research-loop.yml` runs a cycle on a timer on
    GitHub's infrastructure and commits the result. If the schedule is disabled, the
    engine stops; nothing runs on its own.
19. **Budgets are small on purpose.** A cycle is capped at 60 HTTP requests, 900
    seconds, four questions and three experiments. A run that hits a cap records that
    it stopped early.
20. **Four sources need credentials that are not configured** (`eia`, `fred`, `ncei`,
    `patentsview`). Until keys are provided, questions that would use them record a
    `credential_required` status instead of silently returning nothing.
21. **The build environment could not reach most sources.** In the sandbox used to
    produce the published run, egress was limited to GitHub, PyPI and npm, so arXiv,
    Crossref, Hacker News, OpenAlex and Semantic Scholar were unreachable. The run
    recorded that as a warning; the topic pages openly say that only GitHub answered.
    On GitHub Actions, where egress is unrestricted, this limit does not apply - but
    the published pages from *this* run still reflect it.
22. **The library never forgets and never compacts.** Streams are append-only; a
    superseded claim stays in `library/claims.jsonl` with its history. Growth is
    unbounded and there is no pruning tool yet.
23. **Files are the source of truth; the database is an optional mirror.** The
    default store is still append-only JSONL - auditable, diffable, portable.
    Since 2026-09-22 `python3 -m selflearn storage sync|verify` mirrors every
    stream into SQLite (standard library) or PostgreSQL (optional `psycopg`
    driver) and proves the two views identical row for row, and
    `python3 -m selflearn retrieve` searches claims through a deterministic
    TF-IDF vector index. `site --from-database` and `run --from-database` build
    the published site from the mirror - refused unless the views agree - and
    the scheduled workflow publishes every cycle that way. Not yet done: a run
    against a live PostgreSQL server - none exists in this build environment and
    none can be installed here, so that driver path is proven only by its
    documented DB-API shape and its missing-driver error. The graph database and
    Redis from the design document's reference stack remain deliberately
    unused.

## Coverage of the brief itself

24. **New topics are proposed from the engine's own retrieval, not from the web.**
    Topic invention now exists (`selflearn/think/invention.py`): phrases recurring in at
    least two retrieved documents are scored as novelty x importance x potential and can
    be promoted to a question, with every candidate and its components published. But the
    candidate pool is what this engine has retrieved, not an open crawl, so "novel" means
    novel to this library and a topic that is new to the world but absent from the
    retrieved documents will never be proposed. The seed list
    `data/seeds/topics.json` remains human-authored. Section 12 of the design document is
    marked partial for that reason.
25. **"Nonstop" is a schedule, not a promise.** The design document itself asks for
    event-driven operation rather than a process that never exits. The engine matches
    that reading; anyone expecting a permanently-running daemon will be disappointed.
26. **The claim set skews to metadata.** With only GitHub reachable from the build
    sandbox, most accepted claims are registry facts - repository descriptions, star
    counts, languages, licences, activity dates. That is genuine evidence, quoted and
    attributable, but it is not domain knowledge. The engine's usefulness scales with
    the number of sources it can reach, which is why the source layer is the first
    thing to fix (see `docs/ROADMAP.md`).

27. **Cross-document synthesis currently composes nothing.** The layer exists and is
    tested, but its rules require two different sources and a shared subject, and with one
    reachable source neither can be satisfied. Every statement the earlier, weaker rules
    produced was retired rather than left published: 24 of them are listed under "Retired
    statements" on the pages that carried them, each with the reason, and none is counted as
    a current finding. The layer will start producing statements when a second source is
    reachable, which is a consequence of limitation 26 (the claim set skews to
    metadata) rather than of the rules.
28. **A retired statement stays in the library, and takes its dependents with it.**
    `Claim.superseded` marks a statement a later cycle no longer produces; the record is never
    deleted, the verification result is never rewritten, and the audit reports how many are
    excluded from re-verification. Briefs that quote a retired claim, criticisms of those
    briefs and gap questions about that claim are withdrawn the same way
    (`loop.retire_dependents`), because a brief is an inference over the claims it quotes and
    cannot outlive them. Every withdrawn record is listed under "Retired statements" on the
    topic page that carried it, with the reason. A reviewer who believes a retired statement
    was correct can read the reason on the record and say so - but there is no tool to
    reinstate one yet.
29. **Withdrawal is one-directional and has no undo.** Nothing in the engine can restore a
    superseded claim, brief, criticism or question to current status. Reinstating one means
    editing the JSON line by hand, which the audit would then report as a claim whose record
    does not match its history.
30. **All twelve keyed sources now have transcribed credential mechanisms - but
    transcribed is not proven live.** The six that were outstanding on the morning
    of 2026-09-22 (`census_us`, `doaj`, `nvd`, `pubmed`, `semantic_scholar`,
    `stackexchange`) were transcribed from the operator's own documentation that
    afternoon - each with a verbatim quote and a verification date in
    `CREDENTIAL_MECHANISMS` and `docs/SOURCES.md` - so
    `declared_but_not_transmitted` is empty. The same review found `PubMedSource`
    omitting the key on its second-stage `efetch` request; both stages now send it.
    The `declared, not sent` label remains in the code so any future registration
    without a transcription is published as such rather than assumed to work.
    No key except `GITHUB_TOKEN` is configured in this environment, so eleven of the
    twelve have never carried their credential on a real request from this
    repository.
31. **URL reachability does not equal semantic validity.** The automated link check
    verifies that an HTTP endpoint or documentation URL resolves and records its status
    code (103 of 120 resolved on unrestricted runners). It does not parse the page
    content to confirm that an operator hasn't rewritten their schema or changed their terms.
    Where exact quotes are required (such as credential methods), they are quoted
    verbatim in `CREDENTIAL_MECHANISMS` with verification dates.
32. **Upstream operator outages cannot be fixed internally.** During the link audit,
    IMF's documentation domain (`datahelp.imf.org`) failed DNS lookup from multiple
    independent networks, and `https://api.imf.org/` returned HTTP 502. The engine
    flags this irregularity for manual human review rather than guessing an alternative
    or substituting unverified third-party aggregators.
33. **An offline cycle spends the per-topic evidence budget on the first source in
    the reading list.** `max_evidence_per_topic` (12) caps how many documents one
    topic collects; when the first source's stored snapshots replay 12 records the
    collector stops, so the remaining sources in that topic's list are never
    attempted and the cycle's source-status table lists only that first source.
    Cycle `run-e5bee75a9789` shows the shape directly: `0 of 1 polled source(s)
    responded live`. A live cycle rarely trips this because a reachable source
    usually returns fewer than 12 items per query; a snapshot cycle must therefore
    not be read as a coverage report - the coverage report is what a live cycle on
    an unrestricted runner writes.

34. **The access-policy gate can only be as honest as the network it runs on.**
    `selflearn/fetch/robots.py` implements RFC 9309 literally, and 2.3.1.4 says an
    unreachable `robots.txt` means complete disallow. In the sandbox that produced
    the published run, most hosts close the TLS session at egress, so 34 of the 38
    recorded decisions are `unreachable_disallowed`: a true record of what *this
    machine* could read, not a statement about those operators. The first scheduled
    cycle on a GitHub runner replaces it, and the page prints when each decision was
    made and which run made it.
35. **The gate matches the path, not the query string.** RFC 9309 2.2.2 speaks of
    "the path", while its Figure 4 lists `/foo/bar?baz=quz` in a column headed "Path
    to Match" - the standard is ambiguous here. This engine matches the path only and
    publishes that choice in the module docstring, on the sources page and in
    `docs/SOURCES.md`. An operator whose rules depend on query parameters would be
    read more permissively than it intends.
36. **A refusal is published, never worked around - including when the refusal is
    wrong for this project.** PyPI's JSON API is documented by its operator and
    disallowed to every crawler by the same operator's `robots.txt`, so the engine
    uses the two RSS feeds the operator's API page recommends instead. That costs
    per-project search: the feeds are global and unqueryable, so PyPI evidence arrives
    as "what is new on PyPI" rather than "what PyPI says about this question". The
    relevance filter drops what does not bear on the question and reports how much it
    dropped. No mirror, proxy or alternative host is substituted for a refused route.
