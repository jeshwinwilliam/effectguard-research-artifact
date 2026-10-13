from __future__ import annotations

from pathlib import Path

from effectguard.p4.benchmark import load_development_benchmark
from effectguard.p4.common_execution import CommonWorkflowSpec, _read_properties, run_effectguard_common_arm
from effectguard.p4.local_provider import FaultScript, LocalEffectProvider


BENCHMARK = load_development_benchmark(Path("experiments/p4/development_benchmark_v1.json"))


def _scenario(task_id: str):
    return next(scenario for scenario in BENCHMARK.scenarios if scenario.task_id == task_id)


def test_common_spec_is_deterministic_and_preserves_the_development_graph() -> None:
    scenario = _scenario("procurement_positive_gap_success")

    first = CommonWorkflowSpec.from_scenario(scenario, pair_namespace="development-pair-1")
    second = CommonWorkflowSpec.from_scenario(scenario, pair_namespace="development-pair-1")

    assert first.graph_sha256 == second.graph_sha256
    assert first.logical_operation_id == "development-pair-1:reserve-a"
    assert first.action_ids == ("reserve-b", "ship-b", "tax")
    assert first.root_compensation_required is False
    assert first.root_compensation_supported is False


def test_effectguard_common_arm_uses_provider_observations_and_independent_evaluation(tmp_path) -> None:
    scenario = _scenario("travel_positive_gap_success")
    specification = CommonWorkflowSpec.from_scenario(scenario, pair_namespace="development-pair-2")

    provider = LocalEffectProvider(tmp_path / "provider.sqlite")
    try:
        result = run_effectguard_common_arm(scenario, specification, provider)
    finally:
        provider.close()

    assert result.initial_status == "BLOCKED"
    assert result.terminal_status == "RECOVERED"
    assert result.graph_sha256 == specification.graph_sha256
    assert result.evaluator is not None
    assert result.evaluator.passes is True
    assert result.duplicate_external_effect is False


def test_common_arm_retries_only_provider_declared_transient_failures(tmp_path) -> None:
    scenario = _scenario("travel_positive_gap_success")
    specification = CommonWorkflowSpec.from_scenario(scenario, pair_namespace="development-retry")
    provider = LocalEffectProvider(
        tmp_path / "provider.sqlite",
        fault_script=FaultScript("common-retry", submit_failures_before_commit=1),
    )
    try:
        result = run_effectguard_common_arm(scenario, specification, provider)
    finally:
        provider.close()

    assert result.terminal_status == "RECOVERED"
    assert result.metrics is not None
    assert result.metrics.retry_attempts == 1


def test_common_arm_retains_duplicate_and_unknown_development_outcomes(tmp_path) -> None:
    duplicate_scenario = _scenario("cloud_duplicate_delivery")
    duplicate_specification = CommonWorkflowSpec.from_scenario(duplicate_scenario, pair_namespace="development-pair-3")
    provider = LocalEffectProvider(tmp_path / "duplicate.sqlite")
    try:
        duplicate = run_effectguard_common_arm(duplicate_scenario, duplicate_specification, provider)
    finally:
        provider.close()

    timeout_scenario = _scenario("cloud_unknown_timeout")
    timeout_specification = CommonWorkflowSpec.from_scenario(timeout_scenario, pair_namespace="development-pair-4")
    provider = LocalEffectProvider(tmp_path / "timeout.sqlite")
    try:
        timeout = run_effectguard_common_arm(timeout_scenario, timeout_specification, provider)
    finally:
        provider.close()

    assert duplicate.duplicate_external_effect is True
    assert duplicate.terminal_status == "RECOVERY_UNSUPPORTED"
    assert timeout.terminal_status == "UNRESOLVED"
    assert timeout.evaluator is not None
    assert timeout.evaluator.passes is True


def test_temporal_witness_properties_restore_logical_identifiers(tmp_path) -> None:
    witness = tmp_path / "temporal.properties"
    witness.write_text("logical_operation_id=pair\\:travel\\:flight-a\n", encoding="latin-1")

    assert _read_properties(witness)["logical_operation_id"] == "pair:travel:flight-a"
