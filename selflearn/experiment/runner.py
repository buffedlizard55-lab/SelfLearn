"""Run an experiment script in a subprocess and turn the result into evidence.

Safety and traceability
-----------------------
* The script is hashed before and after execution; a mismatch means the file was
  modified while running and the result is discarded.
* The process runs with a timeout, a temporary output file, and a minimal
  environment (no inherited credentials are passed through except ``PATH`` and
  ``PYTHONPATH`` that the interpreter needs).
* The full stdout and stderr are captured and stored, so a failed experiment is
  as reviewable as a successful one.
* The result becomes an :class:`~selflearn.models.EvidenceRecord` of class
  ``direct_experiment`` - rank 1, the strongest class in the hierarchy - and its
  rendered text is what later claims quote.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..config import ROOT
from ..models import EvidenceRecord, ExperimentResult
from ..util import sha256_text, stable_id, to_jsonable, utcnow_iso
from .catalogue import ExperimentSpec

MAX_CAPTURE = 6000


@dataclass
class ExperimentRun:
    spec: ExperimentSpec
    seed: int
    command: str
    script_sha256: str
    script_sha256_after: str
    returncode: int
    stdout: str
    stderr: str
    duration_seconds: float
    result: dict[str, Any] = field(default_factory=dict)
    error: str = ""

    @property
    def status(self) -> str:
        if self.error:
            return "failed"
        if not self.result:
            return "inconclusive"
        conclusion = str(self.result.get("conclusion", ""))
        if "falsified" in conclusion:
            return "completed"
        return "completed" if conclusion else "inconclusive"

    @property
    def tampered(self) -> bool:
        return bool(self.script_sha256_after) and self.script_sha256 != self.script_sha256_after

    def to_dict(self) -> dict[str, Any]:
        return {
            "experiment_id": self.spec.experiment_id,
            "seed": self.seed,
            "command": self.command,
            "script_sha256": self.script_sha256,
            "script_sha256_after": self.script_sha256_after,
            "tampered": self.tampered,
            "returncode": self.returncode,
            "duration_seconds": round(self.duration_seconds, 3),
            "status": self.status,
            "stdout": self.stdout[:MAX_CAPTURE],
            "stderr": self.stderr[:MAX_CAPTURE],
            "result": to_jsonable(self.result),
            "error": self.error,
        }


def _hash_file(path: Path) -> str:
    try:
        return sha256_text(path.read_text(encoding="utf-8"))
    except OSError:
        return ""


def run_experiment(
    spec: ExperimentSpec,
    *,
    root: Path | None = None,
    seed: int | None = None,
    timeout: int | None = None,
    python: str | None = None,
) -> ExperimentRun:
    """Execute one experiment script and capture everything it produced."""
    root = Path(root or ROOT)
    script = root / spec.script
    seed = spec.seeds[0] if seed is None else seed
    timeout = timeout or spec.timeout_seconds
    python = python or sys.executable

    if not script.exists():
        return ExperimentRun(
            spec=spec,
            seed=seed,
            command="",
            script_sha256="",
            script_sha256_after="",
            returncode=-1,
            stdout="",
            stderr="",
            duration_seconds=0.0,
            error=f"script not found: {spec.script}",
        )

    before = _hash_file(script)
    with tempfile.TemporaryDirectory(prefix="selflearn-exp-") as tmp:
        out_path = Path(tmp) / "result.json"
        command = [python, str(script), "--seed", str(seed), "--out", str(out_path)]
        env = {
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "PYTHONPATH": str(root),
            "PYTHONDONTWRITEBYTECODE": "1",
            "HOME": tmp,
            "TMPDIR": tmp,
            "LANG": os.environ.get("LANG", "C.UTF-8"),
        }
        started = time.monotonic()
        error = ""
        stdout = stderr = ""
        returncode = -1
        try:
            completed = subprocess.run(
                command,
                cwd=str(root),
                env=env,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            returncode = completed.returncode
            stdout = completed.stdout or ""
            stderr = completed.stderr or ""
        except subprocess.TimeoutExpired as exc:
            error = f"experiment exceeded the {timeout} second budget"
            stdout = (exc.stdout or b"").decode("utf-8", "replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            stderr = (exc.stderr or b"").decode("utf-8", "replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        except OSError as exc:
            error = f"could not start the experiment process: {exc}"
        duration = time.monotonic() - started

        payload: dict[str, Any] = {}
        if not error and out_path.exists():
            try:
                payload = json.loads(out_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                error = f"result file was not valid JSON: {exc}"
        elif not error and returncode != 0:
            error = f"experiment exited with status {returncode}"

    after = _hash_file(script)
    run = ExperimentRun(
        spec=spec,
        seed=seed,
        command=" ".join(command),
        script_sha256=before,
        script_sha256_after=after,
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
        duration_seconds=duration,
        result=payload,
        error=error,
    )
    if run.tampered and not run.error:
        run.error = "the experiment script changed while it was running; the result is discarded"
        run.result = {}
    return run


def render_experiment_text(run: ExperimentRun) -> str:
    """Plain-text rendering of an experiment result, used as citable evidence.

    Every line is produced directly from the result JSON, so a claim extracted
    from this text is verifiable against it by construction.
    """
    result = run.result
    lines = [
        f"Source: SelfLearn direct experiment {run.spec.experiment_id}",
        f"Title: {run.spec.title}",
        f"Experiment purpose: {run.spec.purpose} experiment",
        f"Hypothesis: {result.get('hypothesis') or run.spec.hypothesis}",
        f"Falsifier: {result.get('falsifier') or run.spec.falsifier}",
        f"Method: {result.get('method', '')}",
        f"Metric: {result.get('metric') or run.spec.metric}",
        f"Baseline: {result.get('baseline_name', 'baseline')} = {result.get('baseline')}",
        f"Best variant: {result.get('best_variant')} = {result.get('best_value')}",
    ]
    for variant in result.get("variants", []) or []:
        lines.append(f"Variant result: {variant.get('name')} = {variant.get('value')}")
    for check in result.get("checks", []) or []:
        outcome = "passed" if check.get("outcome") else "failed"
        lines.append(f"Check {outcome}: {check.get('check')} (observed {check.get('observed')})")
    if result.get("conclusion"):
        lines.append(f"Conclusion: {result['conclusion']}")
    if result.get("limitation"):
        lines.append(f"Limitation: {result['limitation']}")
    else:
        lines.append("Limitation: a computational result; it does not measure any physical system.")
    environment = result.get("environment") or {}
    if environment:
        lines.append(
            "Environment: " + ", ".join(f"{key}={value}" for key, value in sorted(environment.items()) if value is not None)
        )
    lines.append(f"Seed: {run.seed}")
    lines.append(f"Reproduce with: {run.command}")
    lines.append(f"Script sha256: {run.script_sha256}")
    lines.append(f"Ran at: {utcnow_iso()}")
    return "\n".join(lines)[:6000]


def to_result(run: ExperimentRun, topic_id: str) -> ExperimentResult:
    return ExperimentResult(
        experiment_id=run.spec.experiment_id,
        topic_id=topic_id,
        hypothesis=str(run.result.get("hypothesis") or run.spec.hypothesis),
        method=str(run.result.get("method") or ""),
        command=run.command,
        script_path=run.spec.script,
        script_sha256=run.script_sha256,
        metric=str(run.result.get("metric") or run.spec.metric),
        baseline=_as_float(run.result.get("baseline")),
        best_variant=str(run.result.get("best_variant") or "") or None,
        best_value=_as_float(run.result.get("best_value")),
        seed=run.seed,
        result_json=to_jsonable(run.result),
        status=run.status,
        error=run.error,
    )


def to_evidence(run: ExperimentRun, topic_id: str) -> EvidenceRecord:
    text = render_experiment_text(run)
    evidence_id = stable_id("ev", "selflearn", run.spec.experiment_id, run.script_sha256[:16], str(run.seed))
    return EvidenceRecord(
        evidence_id=evidence_id,
        source_id="selflearn_experiment",
        source_name="SelfLearn direct experiment",
        url=f"https://github.com/buffedlizard55-lab/SelfLearn/blob/main/{run.spec.script}",
        title=f"Direct experiment: {run.spec.title}",
        text=text,
        content_hash=sha256_text(text),
        evidence_class="direct_experiment",
        evidence_rank=1,
        published_at=utcnow_iso()[:10],
        license="MIT (this repository)",
        publisher="SelfLearn",
        is_fixture=False,
        is_live=True,
        notes=(
            f"Run by this engine with seed {run.seed}. Reproduce with: {run.command}. "
            f"Script hash {run.script_sha256[:19]}."
        ),
    )


def _as_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
