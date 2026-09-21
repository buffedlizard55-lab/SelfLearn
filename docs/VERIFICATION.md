# Verification

The promise this project makes is narrow and testable: *nothing is published as a
fact unless it can be quoted from a retrieved document, and any number in that
statement appears in that document*. This document explains how that promise is
enforced, what the checks measure, and — just as importantly — what they cannot see.

## Where a claim comes from

1. `fetch/collector.py` retrieves a document and writes it to
   `evidence/snapshots/<evidence_id>.json` with its SHA-256 hash, HTTP status,
   licence and retrieval time.
2. `verify/grounding.py` splits the document's text into sentences, drops
   scaffolding lines and content-free sentences, and offers the rest as candidate
   claims. The candidate's text *is* a span of the document; nothing is paraphrased.
3. `verify/verifier.py` compares the candidate against the whole stored document and
   returns a verdict with reasons.
4. A claim is written to `library/claims.jsonl` with its verdict, the document it came
   from, and the quoted span.

Because step 2 cuts rather than rewrites, the engine cannot introduce a fact that was
not in the document. The verifier's job is to catch the two ways that could still go
wrong: a span that is misleading in context, and a number that does not belong.

## The rules, in order of precedence

**Hard failures — never overridden by a good score**

1. A numeric literal in the claim that does not appear in the document.
2. A date literal in the claim that does not appear in the document.
3. A polarity mismatch: the passage of the document that overlaps the claim most
   contains a negation the claim does not reflect, or the reverse.

**Caps — the claim is shown, but as *needs review***

4. Direction of change reversed: the claim says a quantity rose and the overlapping
   passage says it fell (or an equivalent pair: improve/degrade, higher/lower,
   more/less, support/undermine, and others listed in `verify/verifier.py`).
5. Strength mismatch: a claim stated as universal ("all", "every", "never") against a
   passage that hedges ("about", "roughly", "some", "may", "estimated").

**Acceptance**

6. A verbatim quote of at least the minimum quote length appears in the document →
   `supported`.
7. Otherwise the share of the claim's content tokens that appear in the document must
   reach the support threshold → `supported`; above the partial threshold →
   `partially_supported`; below → `unsupported`.

The thresholds in force are published on the site and stored in
`state/calibration.json`. As of the run that produced this site they are:

| Setting | Value | Meaning |
| --- | --- | --- |
| `supported` | 0.80 | token coverage needed for a claim to be published as supported |
| `partially_supported` | 0.45 | coverage needed to keep the claim at all, marked for review |
| `quote_min_chars` | 24 | minimum length for a verbatim quote to count on its own |

## What this looks like in practice

Every line below was produced by running `verify_claim` against a stored document;
`python3 -m selflearn selftest` exercises the same rules as unit tests.

| Probe | Verdict | Reason recorded |
| --- | --- | --- |
| Verbatim span of the document | `supported` | "Verbatim quoted span found in the document." |
| "gained 42% more stargazers" against a document that never mentions 42% | `unsupported` | "Hard failure: numeric literals absent from the document: 42%." (coverage was 0.71 — the score does not rescue it) |
| `1,200` in the claim against `1200` in the document | `supported` | numeric literals canonicalise, so formatting is not a false rejection |
| `2 percent` against `2%` | `supported` | same canonicalisation for percentages |
| "The tool improves battery capacity degradation" against a passage that says degradation happens | `partially_supported` | "Capped to partially supported: claim says 'improv' while the overlapping passage says 'degrad'." |
| "in all climates" against a passage that says "about 2% per year in temperate climates" | `partially_supported` | "Capped to partially supported: claim is stated as universal while the overlapping passage hedges with 'about'." |

## Calibration

`data/fixtures/verification_cases.jsonl` holds 26 hand-labelled cases: verbatim
quotes, fabricated figures, wrong years, offsets of one year, unit substitution,
negation in either direction, direction reversal, universality against hedging, empty
claims, empty documents, unrelated subjects, unicode typography, separator formats and
deliberately content-free filler. Each case records the expected verdict and a
one-sentence rationale written by hand.

`python3 -m selflearn calibrate` sweeps the threshold grid and reports, for each
candidate, the number of disagreements, the false supports (cases labelled
`unsupported` that were accepted) and the macro F1. The selection rule is not
"maximise accuracy": **zero false supports comes first**, then accuracy. Measured on
the 26 cases:

| Metric | Value |
| --- | --- |
| Cases | 26 |
| Accuracy at the selected point | 1.00 |
| Macro F1 at the selected point | 1.00 |
| False supports at the selected point | 0 |
| Accuracy of the default thresholds before calibration | 0.96 |
| Cases excluded from selection | 1 (the unit-substitution case, documented below) |

The one excluded case is excluded *visibly*: it stays in the file, carries an
exclusion reason, and the test suite asserts that it is still there. Removing a case
the engine fails would be the dishonest move; publishing it is the point.

## Derived claims

Some statements are about the engine's own library — "this question is currently
supported by twelve verified claims drawn from two independent sources". These are
marked `claim_kind=derived`, they record the figures they were computed from on the
claim itself (`context_numbers`), and they are checked by
`verify/verifier.py::verify_derived`, which requires every number in the sentence to
be one of the recorded figures. The audit re-computes them from the recorded figures
and raises an error if the verdict changes. A derived claim never cites a document,
and the audit raises an error if one appears without its figures.

## Independent checks a reviewer can run

| Check | Command |
| --- | --- |
| Re-verify every claim from its stored snapshot | `python3 -m selflearn audit` |
| See the labelled cases and the calibration sweep | `python3 -m selflearn calibrate` |
| Confirm the thresholds in force | `python3 -m selflearn status` |
| Confirm a source is reachable and what it returned | `python3 -m selflearn sources --probe` |
| Re-run the whole suite (65 tests) | `python3 -m selflearn selftest` |

## What the verifier cannot see

These are limits, not bugs in progress. They are the reason every claim carries a
verdict badge rather than being presented as settled.

1. **Unit substitution.** "50 dollars per kilowatt hour" against a document that says
   "50 euros per kilowatt hour" matches on tokens and on the number. Detected: no.
   (Labelled case `c23`, excluded from calibration and published as a known gap.)
2. **Paraphrase that changes meaning while keeping the words.** Synonym swaps with
   opposite implications survive the token test if the surrounding sentence is similar.
3. **Irony, sarcasm and quotation of a disputed claim.** A document reporting what a
   third party claims looks the same as the document asserting it.
4. **Multi-document synthesis.** The verifier checks one claim against one document.
   Conclusions that require joining two documents are not produced by this engine at
   all, so they cannot be over-claimed — but they are also not available.
5. **Language and translation.** Token overlap is English-centric and casefolded;
   non-English documents or translations are not handled.
6. **Table and figure semantics.** A number extracted from a rendered table keeps its
   digits but not necessarily its column meaning.
7. **Anything outside the retrieved text.** If the relevant caveat is in a linked
   appendix the engine did not retrieve, the claim can still be accepted.

Each of these is repeated in `docs/LIMITATIONS.md` with the mitigation that exists,
if any.
