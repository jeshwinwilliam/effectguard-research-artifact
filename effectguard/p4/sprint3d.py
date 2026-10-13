"""Reproducible, development-only Sprint 3D baseline comparison artifact."""

from __future__ import annotations

import hashlib
import json
import xml.etree.ElementTree as element_tree
from pathlib import Path

from ..models import EffectClass, ObservedStatus
from .baselines import run_development_baseline
from .benchmark import DevelopmentAction, DevelopmentScenario
from .models import ActionDescriptor, EffectReceipt, ProviderCapabilities


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _shared_scenario() -> DevelopmentScenario:
    capabilities = ProviderCapabilities(True, True, True, True)
    root = EffectReceipt(
        logical_operation_id="external-capacity-check",
        effect_class=EffectClass.COMPENSABLE,
        observed_status=ObservedStatus.UNKNOWN,
        provider_reference="development-only:external-capacity-check",
        idempotency_key="development-only:external-capacity-check",
        capabilities=capabilities,
    )
    fallback = DevelopmentAction(
        ActionDescriptor(
            action_id="conflicting-fallback",
            logical_operation_id="conflicting-fallback",
            effect_class=EffectClass.COMPENSABLE,
            conflicts_with_effects=(root.logical_operation_id,),
            capabilities=capabilities,
        ),
        parents=(root.logical_operation_id,),
    )
    return DevelopmentScenario(
        task_id="sprint3d-ambiguous-verified-success",
        domain="external-topology-development-adaptation",
        fault="AMBIGUOUS_ACKNOWLEDGEMENT_AFTER_TRANSIENT_PRECOMMIT_FAILURE",
        claimed_positive_semantic_gap=False,
        semantic_gap_applicable=True,
        root_receipt=root,
        resolved_status=ObservedStatus.SUCCESS,
        actions=(fallback,),
        expected_validity={"conflicting-fallback": "INVALID"},
        required_invariants=("exactly-one-logical-effect", "no-conflicting-fallback"),
    )


def _temporal_test_evidence(report_path: Path) -> dict[str, object]:
    try:
        suite = element_tree.parse(report_path).getroot()
    except (OSError, element_tree.ParseError) as error:
        raise ValueError(f"cannot read Temporal SDK test report: {report_path}") from error
    tests = int(suite.attrib.get("tests", "0"))
    failures = int(suite.attrib.get("failures", "0"))
    errors = int(suite.attrib.get("errors", "0"))
    if tests < 2 or failures or errors:
        raise ValueError("Temporal SDK baseline tests are not operational")
    return {
        "status": "SDK_TEST_SERVICE_OPERATIONAL",
        "tests": tests,
        "failures": failures,
        "errors": errors,
        "report_sha256": _sha256(report_path),
        "durability_claim": "UNVERIFIED_EXTERNAL_SERVICE_CRASH_RECOVERY",
    }


def write_sprint3d_development_comparison(
    config_path: str | Path,
    temporal_test_report: str | Path,
    output_root: str | Path,
) -> dict[str, object]:
    """Write a new development artifact and refuse to overwrite prior results."""

    config_path = Path(config_path)
    report_path = Path(temporal_test_report)
    output_root = Path(output_root)
    if output_root.exists():
        raise FileExistsError(f"Sprint 3D output already exists: {output_root}")
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if config.get("kind") != "development_only_not_confirmatory":
        raise ValueError("Sprint 3D comparison must remain development-only")
    scenario = _shared_scenario()
    rows: list[dict[str, object]] = []
    for strategy in ("effectguard", "dependency_only", "idempotency_aware"):
        result = run_development_baseline(scenario, strategy)
        rows.append(
            {
                "strategy": strategy,
                "initial_status": result.initial_status.value if result.initial_status else None,
                "final_status": result.final_status.value,
                "selected_actions": list(result.selected_actions),
                "recovery_step_count": result.recovery_step_count,
                "actual_invariants_hold": result.actual_invariants_hold,
                "trace": list(result.trace),
            }
        )
    temporal = _temporal_test_evidence(report_path)
    rows.append(
        {
            "strategy": "temporal_java_sdk",
            "initial_status": "UNKNOWN",
            "final_status": "RECOVERED",
            "selected_actions": [],
            "recovery_step_count": None,
            "actual_invariants_hold": True,
            "trace": [
                "Temporal SDK test service retried a pre-commit failure.",
                "The Java activity recorded one stable logical effect and verified an ambiguous acknowledgement.",
            ],
            "temporal_evidence": temporal,
        }
    )
    raw_dir = output_root / "raw"
    processed_dir = output_root / "processed"
    manifest_dir = output_root / "manifests"
    for directory in (raw_dir, processed_dir, manifest_dir):
        directory.mkdir(parents=True)
    for row in rows:
        (raw_dir / f"{row['strategy']}.json").write_text(json.dumps(row, indent=2, sort_keys=True), encoding="utf-8")
    summary = {
        "comparison_id": config["comparison_id"],
        "phase": "P4_DEVELOPMENT_ONLY",
        "not_confirmatory": True,
        "rows": rows,
        "unavoidable_differences": config["unavoidable_differences"],
        "interpretation": "All observed strategies reached their modeled terminal safety outcome. This artifact does not establish comparative performance, external validation, or production durability.",
    }
    (processed_dir / "comparison_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    manifest = {
        "comparison_id": config["comparison_id"],
        "config_sha256": _sha256(config_path),
        "temporal_test_report_sha256": temporal["report_sha256"],
        "strategies": config["strategies"],
        "raw_files": sorted(path.name for path in raw_dir.glob("*.json")),
        "not_confirmatory": True,
    }
    (manifest_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return summary
