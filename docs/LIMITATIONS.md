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
   threshold calibration, sorting and search comparison counts, hash collision rates.
   Statements about the world can be sourced, quoted and contradicted, but not tested
   here.
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

## Operational limits

13. **A cycle is a process, not a daemon.** Continuity comes from the schedule that
    starts it: `.github/workflows/research-loop.yml` runs a cycle on a timer on
    GitHub's infrastructure and commits the result. If the schedule is disabled, the
    engine stops; nothing runs on its own.
14. **Budgets are small on purpose.** A cycle is capped at 60 HTTP requests, 900
    seconds, four questions and three experiments. A run that hits a cap records that
    it stopped early.
15. **Four sources need credentials that are not configured** (`eia`, `fred`, `ncei`,
    `patentsview`). Until keys are provided, questions that would use them record a
    `credential_required` status instead of silently returning nothing.
16. **The build environment could not reach most sources.** In the sandbox used to
    produce the published run, egress was limited to GitHub, PyPI and npm, so arXiv,
    Crossref, Hacker News, OpenAlex and Semantic Scholar were unreachable. The run
    recorded that as a warning; the topic pages openly say that only GitHub answered.
    On GitHub Actions, where egress is unrestricted, this limit does not apply - but
    the published pages from *this* run still reflect it.
17. **The library never forgets and never compacts.** Streams are append-only; a
    superseded claim stays in `library/claims.jsonl` with its history. Growth is
    unbounded and there is no pruning tool yet.
18. **No storage layer beyond files.** The design document's reference stack
    (PostgreSQL, a vector store, a graph database, Redis) is deliberately not used.
    Every record is a JSON line. This is auditable and portable, and it does not scale
    past a research log.

## Coverage of the brief itself

19. **New topics are seeded, not discovered.** New *questions* are derived from
    retrieved evidence, and topics move through their lifecycle automatically, but the
    seed list `data/seeds/topics.json` is still human-authored. Section 12 of the
    design document (trending-topic discovery) is therefore marked partial: the
    scoring exists, the open-ended scan of the web does not.
20. **"Nonstop" is a schedule, not a promise.** The design document itself asks for
    event-driven operation rather than a process that never exits. The engine matches
    that reading; anyone expecting a permanently-running daemon will be disappointed.
21. **The claim set skews to metadata.** With only GitHub reachable from the build
    sandbox, most accepted claims are registry facts - repository descriptions, star
    counts, languages, licences, activity dates. That is genuine evidence, quoted and
    attributable, but it is not domain knowledge. The engine's usefulness scales with
    the number of sources it can reach, which is why the source layer is the first
    thing to fix (see `docs/ROADMAP.md`).
