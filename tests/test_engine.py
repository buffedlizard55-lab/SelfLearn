"""Tests for retrieval, memory, competition, tournament, experiments and publishing."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from selflearn.config import EVIDENCE_RANK, THRESHOLDS  # noqa: E402
from selflearn.experiment.catalogue import EXPERIMENTS  # noqa: E402
from selflearn.experiment.runner import render_experiment_text, run_experiment  # noqa: E402
from selflearn.fetch.registry import REGISTRY, registry_summary, source_matrix  # noqa: E402
from selflearn.fetch.sources import build_source, dig, flatten_json, reconstruct_inverted_abstract, summarise_jsonstat  # noqa: E402
from selflearn.learn.store import Library, _stream_paths  # noqa: E402
from selflearn.models import Attack, Claim, EvidenceRecord, ExperimentResult, Strategy, Topic, Verification  # noqa: E402
from selflearn.think.competition import generate_strategies, strategy_numbers_ok  # noqa: E402
from selflearn.think.critic import critique_strategy, has_fatal  # noqa: E402
from selflearn.think.discovery import discover_questions, score_topic  # noqa: E402
from selflearn.think.elo import EloTable  # noqa: E402
from selflearn.think.manager import build_plan, choose_sources  # noqa: E402
from selflearn.think.personas import ALL_PERSONAS, personas_for  # noqa: E402
from selflearn.think.tournament import run_tournament, score_strategy  # noqa: E402
from selflearn.util import sha256_text, stable_id, utcnow_iso  # noqa: E402

DOC = (
    "Source: Example registry\n"
    "Title: Repository record\n"
    "The project provides a research agent that records provenance for every statement. "
    "It reports 1200 stars and was last updated in 2026. "
    "The maintainers state that the tool is limited to computational questions and does not measure physical systems."
)


def make_evidence() -> EvidenceRecord:
    return EvidenceRecord(
        evidence_id="ev-test-1",
        source_id="github",
        source_name="GitHub REST API",
        url="https://api.github.com/repos/example/project",
        title="Repository record",
        text=DOC,
        content_hash=sha256_text(DOC),
        evidence_class="primary_source",
        evidence_rank=EVIDENCE_RANK["primary_source"],
        is_live=True,
        published_at="2026-01-01",
    )


def make_claims(topic: Topic) -> list[Claim]:
    claims = []
    for index, sentence in enumerate(
        [
            "The project provides a research agent that records provenance for every statement.",
            "It reports 1200 stars and was last updated in 2026.",
            "The maintainers state that the tool is limited to computational questions and does not measure physical systems.",
        ]
    ):
        from selflearn.verify.verifier import verify_claim

        verification = verify_claim(sentence, sentence, DOC)
        claims.append(
            Claim(
                claim_id=stable_id("cl", topic.topic_id, index, sentence),
                topic_id=topic.topic_id,
                text=sentence,
                evidence_id="ev-test-1",
                source_name="GitHub REST API",
                url="https://github.com/example/project",
                quote=sentence,
                evidence_class="primary_source",
                evidence_rank=EVIDENCE_RANK["primary_source"],
                confidence="medium",
                verification=verification,
            )
        )
    return claims


class RegistryTests(unittest.TestCase):
    def test_every_source_declares_an_operator_docs_url_and_class(self) -> None:
        for source_id, spec in REGISTRY.items():
            self.assertTrue(spec.operator, source_id)
            self.assertTrue(spec.docs_url.startswith("https://"), source_id)
            self.assertIn(spec.evidence_class, EVIDENCE_RANK, source_id)
            self.assertTrue(spec.name, source_id)

    def test_credential_sources_declare_env_and_key_url(self) -> None:
        for source_id, spec in REGISTRY.items():
            if spec.requires_key:
                self.assertTrue(spec.key_env, f"{source_id} requires a key but names no env var")
                self.assertTrue(str(spec.key_url).startswith("https://"), source_id)

    def test_every_registered_source_has_an_adapter(self) -> None:
        for source_id in REGISTRY:
            adapter = build_source(source_id)
            self.assertIsNotNone(adapter, source_id)

    def test_summary_counts_add_up(self) -> None:
        summary = registry_summary()
        self.assertEqual(summary["total"], len(REGISTRY))
        self.assertEqual(
            len(summary["credential_required"]) + len(summary["open_no_key"]),
            len(REGISTRY),
        )


class SourceParserTests(unittest.TestCase):
    def test_dig_handles_lists_and_missing_paths(self) -> None:
        payload = {"a": {"b": [{"c": 1}]}}
        self.assertEqual(dig(payload, "a.b.0.c"), 1)
        self.assertIsNone(dig(payload, "a.b.5.c"))
        self.assertIsNone(dig(payload, "a.x.y"))

    def test_inverted_abstract_reconstruction_is_ordered(self) -> None:
        inverted = {"battery": [0], "capacity": [1], "fell": [2]}
        self.assertEqual(reconstruct_inverted_abstract(inverted), "battery capacity fell")

    def test_flatten_json_is_bounded_and_readable(self) -> None:
        lines = flatten_json({"a": {"b": 1}, "c": [1, 2]})
        self.assertIn("a.b = 1", lines)
        self.assertIn("c.0 = 1", lines)

    def test_jsonstat_summary_renders_cells(self) -> None:
        payload = {
            "label": "Renewable share",
            "id": ["geo", "time"],
            "size": [2, 2],
            "dimension": {
                "geo": {"category": {"index": {"EU": 0, "DE": 1}, "label": {"EU": "European Union", "DE": "Germany"}}},
                "time": {"category": {"index": {"2020": 0, "2021": 1}, "label": {}}},
            },
            "value": [12.5, None, 15.0, 16.0],
        }
        summary = summarise_jsonstat(payload)
        self.assertIn("Dataset label: Renewable share", summary)
        self.assertIn("12.5", summary)


class MemoryTests(unittest.TestCase):
    def test_stream_paths_resolve_under_any_root(self) -> None:
        paths = _stream_paths(Path("/tmp/example-root"))
        for name, path in paths.items():
            self.assertTrue(str(path).startswith("/tmp/example-root"), f"{name} -> {path}")
            self.assertTrue(str(path).endswith(".jsonl"))

    def test_library_round_trip_dedupes_and_keeps_history(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            library = Library.load(root, run_id="run-1")
            topic = Topic(topic_id="topic-x", title="Test question", slug="test-question", question="Why?")
            library.add_topics([topic])
            claims = make_claims(topic) if False else []
            del claims
            library.add_evidence([make_evidence()])
            reloaded = Library.load(root, run_id="run-2")
            self.assertEqual(len(reloaded.topics), 1)
            self.assertEqual(len(reloaded.evidence), 1)

            # Appending a changed topic must keep one row in memory and two lines on disk.
            topic.status = "competing"
            library.add_topics([topic])
            reloaded = Library.load(root, run_id="run-3")
            self.assertEqual(reloaded.topics["topic-x"].status, "competing")
            lines = (root / "library" / "topics.jsonl").read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), 2)

    def test_claim_round_trip_preserves_verification(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            topic = Topic(topic_id="topic-y", title="T", slug="t", question="Q")
            library = Library.load(root, run_id="run-1")
            claims = make_claims(topic)
            library.add_claims(claims)
            reloaded = Library.load(root, run_id="run-2")
            self.assertEqual(len(reloaded.claims), len(claims))
            first = reloaded.claims[claims[0].claim_id]
            self.assertEqual(first.verification.verdict, "supported")
            self.assertEqual(first.verification.coverage, 1.0)


class CompetitionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.topic = Topic(
            topic_id="topic-z",
            title="Which research agent records provenance?",
            slug="which-research-agent",
            question="Which research agent records provenance for every statement?",
            keywords=["research agent", "provenance"],
        )
        self.claims = make_claims(self.topic)
        self.by_id = {c.claim_id: c for c in self.claims}
        self.evidence = {"ev-test-1": make_evidence()}

    def test_persona_selection_is_deterministic_and_includes_baselines(self) -> None:
        first = personas_for("topic-z", 6)
        second = personas_for("topic-z", 6)
        self.assertEqual([p.code for p in first], [p.code for p in second])
        smaller = personas_for("topic-z", 3)
        codes = {p.code for p in smaller}
        self.assertTrue({"A", "B"} <= codes, codes)
        self.assertEqual(len(smaller), 3)

    def test_candidates_only_quote_cited_claims(self) -> None:
        strategies = generate_strategies(self.topic, self.claims, ALL_PERSONAS)
        self.assertEqual(len(strategies), len(ALL_PERSONAS))
        for strategy in strategies:
            self.assertIn(strategy.status, {"competing", "blocked"})
            ok, unbacked = strategy_numbers_ok(strategy, self.by_id)
            self.assertTrue(ok, f"{strategy.strategy_id} has unbacked numbers: {unbacked}")

    def test_brief_with_no_evidence_declares_itself_blocked(self) -> None:
        strategies = generate_strategies(self.topic, [], ALL_PERSONAS)
        for strategy in strategies:
            self.assertEqual(strategy.status, "blocked")
            self.assertIn("UNKNOWN", strategy.limitations)

    def test_number_guard_catches_an_injected_figure(self) -> None:
        strategies = generate_strategies(self.topic, self.claims, ALL_PERSONAS)
        strategies[0].argument += " The project claims a 97% success rate."
        ok, unbacked = strategy_numbers_ok(strategies[0], self.by_id)
        self.assertFalse(ok)
        self.assertIn("97%", unbacked)

    def test_critics_fire_and_single_source_is_flagged(self) -> None:
        strategies = generate_strategies(self.topic, self.claims, ALL_PERSONAS)
        attacks = []
        for strategy in strategies:
            attacks.extend(
                critique_strategy(
                    strategy,
                    self.by_id,
                    library_claims=self.claims,
                    evidence_index=self.evidence,
                    now_iso=utcnow_iso(),
                )
            )
        rules = {attack.critic.split(":")[0].strip() for attack in attacks}
        self.assertIn("C7", rules, "single-source candidates must be flagged")
        self.assertIn("C3", rules, "declared assumptions must be flagged")
        self.assertTrue(all(attack.statement for attack in attacks))

    def test_fixture_evidence_is_a_fatal_attack(self) -> None:
        fixture = make_evidence()
        fixture.is_fixture = True
        fixture.is_live = False
        strategies = generate_strategies(self.topic, self.claims, ALL_PERSONAS)
        attacks = []
        for strategy in strategies:
            attacks.extend(
                critique_strategy(strategy, self.by_id, library_claims=self.claims, evidence_index={"ev-test-1": fixture})
            )
        self.assertTrue(has_fatal(attacks), "fixture-grounded candidates must be vetoable")

    def test_tournament_ranks_and_records_elo(self) -> None:
        strategies = generate_strategies(self.topic, self.claims, ALL_PERSONAS)
        attacks_by_strategy: dict[str, list[Attack]] = {}
        for strategy in strategies:
            attacks_by_strategy[strategy.strategy_id] = critique_strategy(
                strategy, self.by_id, library_claims=self.claims, evidence_index=self.evidence, now_iso=utcnow_iso()
            )
        with tempfile.TemporaryDirectory() as tmp:
            elo = EloTable.load(Path(tmp) / "elo.json")
            result = run_tournament("topic-z", strategies, self.by_id, self.evidence, attacks_by_strategy, elo=elo)
            self.assertEqual(len(result.ranking), len(strategies))
            self.assertEqual(set(result.scores), {s.strategy_id for s in strategies})
            self.assertTrue(elo.history, "head-to-head results must update the ratings")
            leaderboard = elo.leaderboard("persona-")
            self.assertTrue(leaderboard)
            for strategy in strategies:
                self.assertIn("criteria", strategy.scorecard)
                self.assertIn("total", strategy.scorecard)

    def test_scorecard_labels_heuristic_criteria(self) -> None:
        strategies = generate_strategies(self.topic, self.claims, ALL_PERSONAS)
        strategy = strategies[0]
        table = score_strategy(strategy, self.by_id, self.evidence, [])
        self.assertEqual(table["criteria"]["scalability"]["method"], "heuristic")
        self.assertEqual(table["criteria"]["correctness"]["method"], "measured")
        self.assertFalse(table["criteria"]["experimental_performance"]["value"])

    def test_experiment_improves_the_experimental_criterion(self) -> None:
        strategy = generate_strategies(self.topic, self.claims, ALL_PERSONAS)[0]
        experiment = ExperimentResult(
            experiment_id="exp-1",
            topic_id=self.topic.topic_id,
            hypothesis="h",
            method="m",
            command="c",
            script_path="experiments/x.py",
            script_sha256="sha256:0",
            metric="accuracy",
            baseline=0.5,
            best_variant="v",
            best_value=0.75,
            seed=1,
        )
        without = score_strategy(strategy, self.by_id, self.evidence, [], experiment=None)
        with_exp = score_strategy(strategy, self.by_id, self.evidence, [], experiment=experiment)
        self.assertEqual(without["criteria"]["experimental_performance"]["value"], 0.0)
        self.assertGreater(with_experiment := with_exp["criteria"]["experimental_performance"]["value"], 0.0)
        self.assertGreater(with_exp["total"], without["total"])
        del with_experiment


class DiscoveryTests(unittest.TestCase):
    def test_questions_are_derived_with_provenance(self) -> None:
        topic = Topic(topic_id="topic-q", title="Capacity", slug="capacity", question="How fast does capacity fall?", keywords=["capacity"])
        claims = make_claims(topic)
        questions = discover_questions(topic, claims, {"ev-test-1": make_evidence()})
        self.assertTrue(questions)
        for question in questions:
            self.assertTrue(question.text)
            self.assertIn(question.origin, {"sub_question", "gap", "discovery", "seed"})

    def test_missing_evidence_produces_a_gap_question(self) -> None:
        topic = Topic(topic_id="topic-empty", title="Empty", slug="empty", question="Anything?", keywords=["anything"])
        questions = discover_questions(topic, [], {})
        self.assertEqual(len(questions), 1)
        self.assertEqual(questions[0].origin, "gap")

    def test_topic_score_reports_unmeasurable_components(self) -> None:
        topic = Topic(topic_id="topic-s", title="S", slug="s", question="Q?", keywords=["q"])
        score = score_topic(topic, [], {})
        self.assertIn("freshness", score.unmeasurable)
        self.assertIn("attention", score.unmeasurable)
        self.assertTrue(score.basis)

    def test_manager_plan_is_bounded_and_explains_itself(self) -> None:
        topics = [
            Topic(topic_id=f"topic-{i}", title=f"Question {i}", slug=f"question-{i}", question="Q?", keywords=["run"])
            for i in range(6)
        ]
        plan = build_plan(topics, {}, {}, run_id="run-x", max_topics=3)
        self.assertEqual(len(plan.selected), 3)
        self.assertEqual(len(plan.tasks), 3)
        for topic in plan.selected:
            self.assertTrue(plan.sources_by_topic[topic.topic_id])

    def test_source_choice_respects_an_explicit_list(self) -> None:
        topic = Topic(topic_id="t", title="T", slug="t", question="Q", keywords=["a"], source_ids=["github", "crossref"])
        self.assertEqual(choose_sources(topic), ["github", "crossref"])


class ExperimentTests(unittest.TestCase):
    def test_catalogue_entries_point_at_real_scripts(self) -> None:
        for spec in EXPERIMENTS:
            self.assertTrue((ROOT / spec.script).exists(), spec.script)
            self.assertTrue(spec.hypothesis and spec.falsifier and spec.metric)

    def test_verification_thresholds_experiment_runs_and_reports(self) -> None:
        spec = next(s for s in EXPERIMENTS if s.experiment_id == "verification-thresholds-v1")
        run = run_experiment(spec, root=ROOT, timeout=300)
        self.assertEqual(run.error, "", run.stderr[-500:])
        self.assertEqual(run.status, "completed")
        self.assertFalse(run.tampered)
        self.assertIn("selected_thresholds", run.result)
        text = render_experiment_text(run)
        self.assertIn("Source: SelfLearn direct experiment", text)
        self.assertIn("Falsifier:", text)
        self.assertIn("Reproduce with:", text)

    def test_search_scaling_experiment_runs(self) -> None:
        spec = next(s for s in EXPERIMENTS if s.experiment_id == "search-scaling-v1")
        run = run_experiment(spec, root=ROOT, timeout=300)
        self.assertEqual(run.error, "")
        self.assertTrue(all(check["outcome"] for check in run.result["checks"]))


class PublishTests(unittest.TestCase):
    def test_site_builds_from_minimal_data(self) -> None:
        from selflearn.publish.site import build_site

        data = {
            "generated_at": utcnow_iso(),
            "run_id": "run-test",
            "mode": "fixture",
            "counts": {"topics": 0, "claims": 0},
            "checks": {},
            "topics": [],
            "sources": {"matrix": source_matrix(), "status": [], "reliability": []},
            "requirements": [],
            "irregularities": [],
            "failures": [],
            "contradictions": [],
            "experiments": [],
            "experiment_catalogue": [],
            "elo": {"leaderboard": []},
            "calibration": {},
            "run_summary": {},
            "methodology": {},
        }
        with tempfile.TemporaryDirectory() as tmp:
            written = build_site(data, Path(tmp))
            names = {path.name for path in written}
            self.assertIn("index.html", names)
            self.assertIn("review.html", names)
            self.assertIn("style.css", names)
            index = (Path(tmp) / "index.html").read_text(encoding="utf-8")
            self.assertIn("SelfLearn", index)
            self.assertIn("no third-party scripts", index)
            self.assertIn("Test run", index, "fixture mode must be visibly labelled")

    def test_root_entry_page_links_into_the_site(self) -> None:
        from selflearn.publish.site import build_site

        data = {
            "generated_at": utcnow_iso(),
            "run_id": "run-test",
            "mode": "live",
            "counts": {"topics": 1, "claims": 2, "documents": 3},
            "topics": [
                {
                    "topic": {
                        "topic_id": "topic-x",
                        "title": "A question",
                        "slug": "a-question",
                        "status": "researching",
                    }
                }
            ],
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            out = root / "docs"
            out.mkdir(parents=True)
            build_site(data, out, write_root_entry=True)
            entry = (root / "index.html").read_text(encoding="utf-8")
            self.assertIn("docs/index.html", entry, "the entry page must link to the site")
            self.assertIn("docs/review.html", entry)
            self.assertIn("docs/topics/a-question.html", entry, "the topic slug must be used, not a title slug")
            self.assertTrue((root / ".nojekyll").exists(), "Pages must serve files as-is")

    def test_rebuild_is_labelled_as_a_rebuild(self) -> None:
        from selflearn.publish.site import build_site

        data = {
            "generated_at": utcnow_iso(),
            "run_id": "run-abc",
            "mode": "live",
            "rebuilt_at": "2026-01-01T00:00:00Z",
            "counts": {},
            "topics": [],
        }
        with tempfile.TemporaryDirectory() as tmp:
            build_site(data, Path(tmp))
            index = (Path(tmp) / "index.html").read_text(encoding="utf-8")
            self.assertIn("run-abc", index)
            self.assertIn("rebuilt from the stored library", index, "a rebuild must not read as a fresh run")

    def test_topic_page_renders_claims_and_unknowns(self) -> None:
        from selflearn.publish.site import build_site

        topic = Topic(topic_id="topic-page", title="A rendered question", slug="a-rendered-question", question="Why?")
        claims = make_claims(topic)
        topic_payload = {
            "topic": topic.to_dict(),
            "statistics": {"claims": len(claims), "supported": len(claims), "sources": 1},
            "claims": [
                {
                    "claim_id": c.claim_id,
                    "text": c.text,
                    "quote": c.quote,
                    "source_name": c.source_name,
                    "url": c.url,
                    "evidence_class": c.evidence_class,
                    "evidence_class_label": "Primary source",
                    "evidence_rank": c.evidence_rank,
                    "confidence": c.confidence,
                    "verdict": c.verification.verdict,
                    "coverage": c.verification.coverage,
                    "quote_match": True,
                    "missing_numbers": [],
                    "reasons": c.verification.reasons,
                    "limitations": "",
                    "recorded_at": c.recorded_at,
                    "evidence_id": c.evidence_id,
                }
                for c in claims
            ],
            "documents": [],
            "derived": [{"text": "This question is currently supported by 3 verified claim(s) drawn from 1 independent source(s).", "label": "library_volume", "context_numbers": ["3", "1"], "limitations": "derived"}],
            "unknowns": [{"question": "What experiment would resolve it?", "answer": "None has been run.", "resolve_with": "Run one."}],
            "strategies": [],
            "attacks": [],
            "questions": [],
            "experiments": [],
            "contradictions": [],
            "tournament": None,
            "winner": None,
            "source_status": [],
            "status_history": [],
        }
        data = {
            "generated_at": utcnow_iso(),
            "run_id": "run-test",
            "mode": "live",
            "topics": [topic_payload],
            "sources": {"matrix": [], "status": [], "reliability": []},
            "requirements": [],
            "irregularities": [],
            "failures": [],
            "contradictions": [],
            "experiments": [],
            "experiment_catalogue": [],
            "elo": {"leaderboard": []},
            "calibration": {},
            "run_summary": {},
            "methodology": {},
            "counts": {},
            "checks": {},
        }
        with tempfile.TemporaryDirectory() as tmp:
            build_site(data, Path(tmp))
            page = (Path(tmp) / "topics" / "a-rendered-question.html").read_text(encoding="utf-8")
            self.assertIn("Verified facts", page)
            self.assertIn("What we do not know", page)
            self.assertIn("Check this page yourself", page)
            self.assertIn(claims[0].text[:40].replace("&", "&amp;"), page)


class AttributionTests(unittest.TestCase):
    """Every claim must travel with the record it came from."""

    def test_scaffolding_lines_are_removed_but_content_survives(self) -> None:
        from selflearn.verify.grounding import strip_scaffolding

        text = (
            "Source: GitHub (https://api.github.com)\n"
            "Record: khoj-ai/khoj\n"
            "Every sentence below names the record it describes. Values are copied from the response without change; "
            "field labels are the adapter's own rendering of the response's field names.\n"
            "The record for khoj-ai/khoj reports: stargazers_count 37457, forks_count 2490, open_issues_count 150.\n"
            "Source note: rate limit 60 requests per hour."
        )
        cleaned = strip_scaffolding(text)
        self.assertNotIn("Source:", cleaned)
        self.assertNotIn("Record: khoj-ai/khoj\n", cleaned)
        self.assertNotIn("Values are copied", cleaned)
        self.assertIn("stargazers_count 37457", cleaned)
        # A source note is adapter commentary, not a statement about the world,
        # so it is stripped too; the audit reports it separately instead.
        self.assertNotIn("rate limit 60 requests", cleaned)

    def test_no_claim_is_engine_metadata(self) -> None:
        from selflearn.verify.grounding import ground_evidence

        record = make_evidence()
        object.__setattr__(
            record,
            "text",
            "Source: GitHub (https://api.github.com)\n"
            "Every sentence below names the record it describes. Values are copied from the response without change; "
            "field labels are the adapter's own rendering of the response's field names.\n"
            "Record: example/project\n"
            "The record for example/project reports: stargazers_count 1200, forks_count 90, language Python.\n"
            "The record for example/project states in its own description: A research agent that records provenance "
            "for every statement it publishes.",
        )
        proposals = ground_evidence(record)
        self.assertTrue(proposals)
        for proposal in proposals:
            self.assertNotIn("Values are copied", proposal.text)
            self.assertFalse(proposal.text.startswith("Record:"))
            self.assertIn("The record for example/project", proposal.text)

    def test_rendered_record_copies_values_with_attribution(self) -> None:
        from selflearn.fetch.sources import render_attributed_record

        rendered = render_attributed_record(
            "khoj-ai/khoj",
            {
                "pushed_at": "2026-08-02T01:55:40Z",
                "stars": "37457",
                "open_issues": "150",
                "description": "Turn any online or local LLM into your personal assistant.",
            },
            source_name="GitHub",
            base_url="https://api.github.com",
            prose_label="description",
            label_overrides={
                "stars": "stargazers_count",
                "open_issues": "open_issues_count",
            },
        )
        self.assertIn("The record for khoj-ai/khoj reports: pushed_at 2026-08-02T01:55:40Z", rendered)
        self.assertIn("stargazers_count 37457", rendered)
        self.assertIn("states in its own description:", rendered)
        self.assertNotIn('"', rendered, "values must not be re-quoted or reformatted")


class VerifySurfaceTests(unittest.TestCase):
    def test_public_exports_resolve(self) -> None:
        import selflearn.verify as verify

        for name in verify.__all__:
            self.assertTrue(hasattr(verify, name), f"{name} is exported but missing")

    def test_derived_claim_round_trips_through_the_audit(self) -> None:
        from selflearn.verify.audit import recheck_claims

        claim = Claim(
            claim_id="cl-derived",
            topic_id="topic-x",
            text="This question is currently supported by 3 verified claim(s).",
            evidence_id="derived-topic-x",
            url="",
            quote="",
            evidence_class="derived_computation",
            evidence_rank=1,
            source_name="SelfLearn library computation",
            claim_kind="derived",
            context_numbers=["3"],
            verification=Verification(verdict="supported", coverage=1.0),
        )
        with tempfile.TemporaryDirectory() as tmp:
            findings = recheck_claims([claim], Path(tmp))
        self.assertEqual(findings, [])

    def test_derived_claim_without_figures_is_an_error(self) -> None:
        from selflearn.verify.audit import check_links

        claim = Claim(
            claim_id="cl-derived",
            topic_id="topic-x",
            text="This question is currently supported by 3 verified claim(s).",
            evidence_id="derived-topic-x",
            url="",
            quote="",
            evidence_class="derived_computation",
            evidence_rank=1,
            source_name="SelfLearn library computation",
            claim_kind="derived",
            context_numbers=[],
        )
        rows = check_links([claim])
        self.assertTrue(any(row.severity == "error" for row in rows))


class PerTopicStatusTests(unittest.TestCase):
    def test_report_shows_only_this_topics_sources(self) -> None:
        from selflearn.models import SourceStatus
        from selflearn.publish.report import build_topic_report

        topic = Topic(topic_id="topic-a", title="A", slug="a", question="Why?")
        other = Topic(topic_id="topic-b", title="B", slug="b", question="Why not?")
        with tempfile.TemporaryDirectory() as tmp:
            library = Library(Path(tmp))
            stamped = SourceStatus(
                source_id="github",
                name="GitHub",
                url="https://api.github.com",
                evidence_class="primary_source",
                evidence_rank=3,
                requires_key=False,
                live_status="reachable",
                topics=["topic-a"],
            )
            unstamped = SourceStatus(
                source_id="arxiv",
                name="arXiv",
                url="https://export.arxiv.org",
                evidence_class="peer_reviewed",
                evidence_rank=4,
                requires_key=False,
                live_status="unreachable",
            )
            report = build_topic_report(library, topic, source_status=[stamped, unstamped])
            ids = {s.source_id for s in report.source_status}
            self.assertIn("github", ids)
            self.assertIn("arxiv", ids, "a status with no topic stamp stays run-wide")
            report_b = build_topic_report(library, other, source_status=[stamped, unstamped])
            ids_b = {s.source_id for s in report_b.source_status}
            self.assertNotIn("github", ids_b)
            self.assertIn("arxiv", ids_b)


if __name__ == "__main__":
    unittest.main()
