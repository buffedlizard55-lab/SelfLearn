"""Long-form content for the published site: methodology, limits, checklists.

Kept as data so that the HTML builder stays a renderer, and so that a reviewer can
diff the wording of the project's own claims about itself.
"""

from __future__ import annotations

DESIGN_DOC_URL = "https://chatgpt.com/share/6ab1612a-2f14-83e8-9de6-808d21a48e53"

# Short labels for the sections of the design document, so that the requirements
# matrix can point at the part of the design each requirement came from. These are
# LABELS, not verbatim quotations of the design document's own headings, and the
# design document itself is linked on the method page.
DESIGN_SECTIONS: dict[int, str] = {
    1: "A world scanner",
    2: "Topic intelligence",
    3: "Multiple independent thinkers",
    4: "The critic is just as important as the researcher",
    5: "Evidence hierarchy",
    6: "Structured memory rather than rewritten memory",
    7: "Every idea gets a lifecycle",
    8: "Automatic experimentation",
    9: "Benchmark everything",
    10: "A research tournament",
    11: "The system needs curiosity",
    12: "Trending-topic discovery",
    13: "A central research manager",
    14: "The final output should be extremely readable",
    15: "The technology stack",
    16: "Event-driven rather than literally nonstop",
    17: "The most important database structure",
    18: "Uncertainty must be expressible",
    19: "Recognising its own knowledge gaps",
    20: "The ultimate architecture",
}

HOW_TO_VERIFY = (
    (
        "Check one claim end to end",
        "Open a topic page, pick a fact, and follow its source link. The quoted span shown on the page must appear "
        "in the linked document. The stored copy of what the engine actually received is in "
        "<span class='mono'>evidence/snapshots/</span>, named by the evidence id shown next to the claim.",
    ),
    (
        "Re-run the verification on the stored bytes",
        "Run <span class='mono'>python -m selflearn audit</span>. It re-derives every claim from the stored snapshot "
        "and reports any claim whose verdict or coverage no longer matches what was published.",
    ),
    (
        "Re-run an experiment",
        "Every experiment row shows the exact command and the sha256 of the script that produced it. Run the command "
        "and compare the JSON output with the stored result.",
    ),
    (
        "Check a number in the prose",
        "Every figure in the generated summaries is listed with the claim or the engine computation it came from. If a "
        "number on a page is not in that list, it is a bug and the audit should have caught it - please report it.",
    ),
    (
        "Check the source register",
        "The sources page lists every registered API with its operator, documentation link, evidence class, whether a "
        "credential is needed, and whether the last run reached it. A source that is not reached is reported there, "
        "not hidden.",
    ),
)

LIMITATIONS = (
    (
        "The engine does not read behind paywalls or logins",
        "Only openly accessible APIs and documents are used. Evidence behind a subscription is absent, and the absence "
        "is recorded as a coverage gap rather than filled with a guess.",
    ),
    (
        "Verification is lexical, not semantic",
        "A claim is checked against a document with string and set operations. This blocks fabricated numbers and "
        "detects polarity flips, but it cannot detect a unit substitution (for example dollars written where the source "
        "says euros) and it cannot judge whether a quoted sentence is being used in the spirit the author intended. "
        "A labelled case in the calibration set documents the unit blind spot explicitly.",
    ),
    (
        "Paraphrase detection is a token heuristic",
        "Coverage is a Jaccard-style token measure. A well-disguised paraphrase that reuses vocabulary will score "
        "high; a faithful paraphrase that uses different vocabulary will score low and be downgraded. The threshold in "
        "force is published, and the calibration set is published with it so it can be re-labelled.",
    ),
    (
        "Contradiction detection produces candidates, not verdicts",
        "Two claims that share vocabulary but assert different numbers, or differ in polarity, are flagged for human "
        "review. The engine does not decide which is right.",
    ),
    (
        "The experiment catalogue is computational",
        "Runnable offline experiments can test statements about algorithms, numerics and the engine's own procedure. "
        "They cannot test statements about the physical world without measured data. Where a question needs physical "
        "measurement, the engine retrieves sources and stops at the boundary of what it can check, saying so.",
    ),
    (
        "Attention and trend signals are weak",
        "Forum and repository activity measures attention, not importance or truth. It is used only to prioritise what "
        "to look at next, and is labelled as a commentary-class signal wherever it appears.",
    ),
    (
        "An autonomous loop needs a scheduler and a budget",
        "The loop runs a bounded number of steps per invocation, within a request and time budget. Continuous "
        "operation therefore comes from an external scheduler: the workflow in "
        "<span class='mono'>.github/workflows/</span> starts a cycle on a timer. The engine itself is deterministic "
        "and needs no credential to run; sources that need a key are reported as "
        "<span class='mono'>credential_required</span> and are never called without one.",
    ),
    (
        "There is no language model anywhere in the pipeline",
        "No model is called at any stage: not to retrieve, not to extract, not to summarise, not to reason. Every "
        "published sentence about the world is a span copied out of a retrieved document, every other sentence is a "
        "count or comparison of the engine's own records, and the scaffolding around them is fixed template text. "
        "This is why the engine cannot synthesise across documents, and why it cannot paraphrase. Adding a model would "
        "require the same numeric and citation guards to be applied to its output before anything was published; that "
        "is on the roadmap and is not implemented.",
    ),
)

REFUSALS = (
    "It will not write a sentence asserting a fact that is not in a retrieved document.",
    "It will not attach a number to a claim unless that exact number appears in the cited text.",
    "It will not present a synthetic fixture as real evidence.",
    "It will not silently drop a source that failed; the failure becomes a review item.",
    "It will not manufacture a conclusion when the evidence is insufficient; it emits UNKNOWN with the reason.",
    "It will not modify the published text of a claim after verification: every change creates a new record.",
)

MEMORY_LAYERS = (
    ("Raw evidence", "library/evidence_index.jsonl and evidence/snapshots/", "Every retrieved document, hashed, with the bytes that were verified."),
    ("Knowledge", "library/claims.jsonl", "Atomic statements, each tied to one document, with its verification result."),
    ("Reasoning", "library/strategies.jsonl, library/attacks.jsonl, library/questions.jsonl", "Competing candidates, the criticism they attracted, and the questions they generated."),
    ("Experiments", "library/experiments.jsonl", "Hypothesis, script, seed, command, result and reproducibility notes for every run."),
    ("Meta-knowledge", "library/discoveries.jsonl, library/failures.jsonl, library/irregularities.jsonl", "Which sources produced usable evidence, which critic rules keep firing, which reasoning patterns keep failing."),
)

REVIEW_CHECKLIST = (
    "Pick any claim and open its source link; confirm the quoted span is in the document.",
    "Compare the claim's coverage score with the threshold in force on the method page.",
    "Open the snapshot file named by the evidence id and confirm the content hash matches.",
    "Re-run one experiment with the command shown and compare the JSON to the stored result.",
    "Read the review page and confirm that every reported irregularity is either fixed or still listed.",
)
