from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from time import perf_counter_ns

from .baselines import DEVELOPMENT_STRATEGIES, DevelopmentBaselineResult, run_development_baseline
from .benchmark import DevelopmentBenchmark, DevelopmentScenario, load_development_benchmark, validate_development_benchmark
from .evaluator import IndependentEvaluator, IndependentTruth


@dataclass(frozen=True)
class DevelopmentPilotSummary:
    benchmark_id: str
    planned_runs: int
    completed_runs: int
    recovered_runs: int
    blocked_runs: int
    unresolved_runs: int
    unsupported_runs: int
    failed_runs: int
    unsafe_runs: int
    evaluator_failures: int
    output_root: str


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _plan_payload(result: DevelopmentBaselineResult) -> dict[str, object]:
    return {
        "preserved_actions": list(result.final_plan.preserved_actions),
        "deferred_actions": list(result.final_plan.deferred_actions),
        "invalid_actions": list(result.final_plan.invalid_actions),
        "recovery_steps": [asdict(step) for step in result.final_plan.recovery_steps],
        "certificates": [
            {
                "action_id": certificate.action_id,
                "result": certificate.result.value,
                "evidence_ids": list(certificate.evidence_ids),
                "reason": certificate.reason,
            }
            for certificate in result.final_plan.certificates
        ],
        "audit_records": [asdict(record) for record in result.final_plan.audit_records],
    }


def _execute_one(scenario: DevelopmentScenario, strategy: str) -> dict[str, object]:
    started = perf_counter_ns()
    result = run_development_baseline(scenario, strategy)
    runtime_validity = {certificate.action_id: certificate.result.value for certificate in result.final_plan.certificates}
    evaluator_truth = IndependentTruth(
        expected_validity=scenario.expected_validity if strategy == "effectguard" else {},
        invariants_hold=result.actual_invariants_hold,
        violated_invariants=() if result.actual_invariants_hold else scenario.required_invariants,
    )
    evaluation = IndependentEvaluator().evaluate(
        runtime_validity=runtime_validity,
        terminal_status=result.final_status.value,
        truth=evaluator_truth,
    )
    return {
        "phase": "P4_DEVELOPMENT_ONLY",
        "task_id": scenario.task_id,
        "domain": scenario.domain,
        "fault": scenario.fault,
        "strategy": strategy,
        "public_context": {
            "root_effect": scenario.root_receipt.logical_operation_id,
            "initial_observed_status": scenario.root_receipt.observed_status.value,
            "resolved_observed_status": scenario.resolved_status.value,
            "provider_capabilities": asdict(scenario.root_receipt.capabilities),
            "required_invariants": list(scenario.required_invariants),
            "graph_descendants": list(scenario.graph_descendants()),
        },
        "runtime_trace": {
            "initial_status": result.initial_status.value if result.initial_status else None,
            "final_status": result.final_status.value,
            "selected_actions": list(result.selected_actions),
            "recovery_step_count": result.recovery_step_count,
            "events": list(result.trace),
            "plan": _plan_payload(result),
        },
        "post_execution_evaluator": {
            "expected_validity": evaluator_truth.expected_validity,
            "invariants_hold": evaluator_truth.invariants_hold,
            "violated_invariants": list(evaluator_truth.violated_invariants),
            "validity_mismatches": list(evaluation.validity_mismatches),
            "recovered_with_invalid_invariants": evaluation.recovered_with_invalid_invariants,
            "passes": evaluation.passes,
        },
        "metrics": {
            "semantic_invalidated_actions": list(scenario.semantic_invalidated_actions()),
            "semantic_gap": len(scenario.graph_descendants()) - len(scenario.semantic_invalidated_actions()),
            "actual_invariants_hold": result.actual_invariants_hold,
            "safety_violation": result.final_status.value == "RECOVERED" and not result.actual_invariants_hold,
            "elapsed_ns": perf_counter_ns() - started,
        },
    }


def execute_development_pilot(config_path: str | Path, output_root: str | Path) -> DevelopmentPilotSummary:
    benchmark = load_development_benchmark(config_path)
    reports = validate_development_benchmark(benchmark)
    root = Path(output_root)
    raw_dir = root / "raw"
    processed_dir = root / "processed"
    manifest_dir = root / "manifests"
    for directory in (raw_dir, processed_dir, manifest_dir):
        directory.mkdir(parents=True, exist_ok=True)

    records: list[dict[str, object]] = []
    for scenario in benchmark.scenarios:
        for strategy in DEVELOPMENT_STRATEGIES:
            record = _execute_one(scenario, strategy)
            records.append(record)
            (raw_dir / f"{scenario.task_id}--{strategy}.json").write_text(
                json.dumps(record, indent=2, sort_keys=True), encoding="utf-8"
            )

    statuses = [record["runtime_trace"]["final_status"] for record in records]
    evaluator_failures = sum(not bool(record["post_execution_evaluator"]["passes"]) for record in records)
    summary = DevelopmentPilotSummary(
        benchmark_id=benchmark.benchmark_id,
        planned_runs=len(benchmark.scenarios) * len(DEVELOPMENT_STRATEGIES),
        completed_runs=len(records),
        recovered_runs=statuses.count("RECOVERED"),
        blocked_runs=statuses.count("BLOCKED"),
        unresolved_runs=statuses.count("UNRESOLVED"),
        unsupported_runs=statuses.count("RECOVERY_UNSUPPORTED"),
        failed_runs=statuses.count("FAILED"),
        unsafe_runs=statuses.count("UNSAFE"),
        evaluator_failures=evaluator_failures,
        output_root=str(root),
    )
    summary_payload = asdict(summary)
    summary_payload["limitations"] = [
        "Deterministic development-only artifact; not a held-out or confirmatory experiment.",
        "Baseline models are transparent abstractions, not integrations with production workflow engines.",
        "No provider, model, Gemini, or external service request was made.",
    ]
    (processed_dir / "summary.json").write_text(json.dumps(summary_payload, indent=2, sort_keys=True), encoding="utf-8")
    manifest = {
        "benchmark_id": benchmark.benchmark_id,
        "benchmark_kind": benchmark.kind,
        "authorship": benchmark.authorship,
        "config_path": str(benchmark.source_path),
        "config_sha256": _sha256(benchmark.source_path),
        "strategies": list(DEVELOPMENT_STRATEGIES),
        "semantic_gap_validation": [asdict(report) for report in reports],
        "planned_runs": summary.planned_runs,
        "raw_files": sorted(path.name for path in raw_dir.glob("*.json")),
    }
    (manifest_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return summary
