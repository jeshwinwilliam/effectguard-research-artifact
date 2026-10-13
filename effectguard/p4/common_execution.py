"""Development-only common execution contract for EffectGuard and Temporal.

The contract deliberately separates a shared workflow specification from each
runtime adapter. The Temporal adapter invokes a real Java Workflow through a
separately managed local Temporal service; it is not a Python policy model.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from time import perf_counter
from typing import Iterable

from ..models import ObservedStatus
from .benchmark import DevelopmentScenario, load_development_benchmark
from .evaluator import IndependentEvaluation, IndependentEvaluator, IndependentTruth
from .fault_schedule import DevelopmentFaultSchedule
from .local_provider import LocalProviderClient, ProviderTransientError
from .models import EffectReceipt, FinalValidationResult, RecoveryRequest, RecoveryTerminalStatus
from .runtime import UnknownSafeRecovery


@dataclass(frozen=True)
class CommonWorkflowSpec:
    """Public development input shared by both runtime adapters."""

    task_id: str
    workflow_id: str
    logical_operation_id: str
    graph_sha256: str
    semantic_graph: str
    resolved_status: str
    duplicate_submission: bool
    root_compensation_required: bool
    root_compensation_supported: bool
    compensation_fails: bool
    evidence_deadline_expired: bool
    action_ids: tuple[str, ...]
    required_invariants: tuple[str, ...]
    fault_schedule: DevelopmentFaultSchedule

    @classmethod
    def from_scenario(cls, scenario: DevelopmentScenario, *, pair_namespace: str) -> "CommonWorkflowSpec":
        graph = {
            "task_id": scenario.task_id,
            "actions": [
                {
                    "action_id": action.descriptor.action_id,
                    "logical_operation_id": action.descriptor.logical_operation_id,
                    "effect_class": action.descriptor.effect_class.value,
                    "parents": action.parents,
                    "requires_effects": action.descriptor.requires_effects,
                    "conflicts_with_effects": action.descriptor.conflicts_with_effects,
                }
                for action in scenario.actions
            ],
            "required_invariants": scenario.required_invariants,
        }
        digest = hashlib.sha256(json.dumps(graph, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
        return cls(
            task_id=scenario.task_id,
            workflow_id=f"{pair_namespace}:{scenario.task_id}",
            logical_operation_id=f"{pair_namespace}:{scenario.root_receipt.logical_operation_id}",
            graph_sha256=digest,
            semantic_graph=";".join(
                "|".join((
                    action.descriptor.action_id,
                    action.descriptor.logical_operation_id,
                    action.descriptor.effect_class.value,
                    str(scenario.root_receipt.logical_operation_id in action.descriptor.requires_effects).lower(),
                    str(scenario.root_receipt.logical_operation_id in action.descriptor.conflicts_with_effects).lower(),
                    str(action.descriptor.capabilities.supports_compensation).lower(),
                ))
                for action in scenario.actions
            ),
            resolved_status=scenario.resolved_status.value,
            duplicate_submission=scenario.duplicate_delivery,
            # Descendant invalidity never implies that the already-observed root
            # effect must be compensated. The shared development schema has no
            # root-compensation requirement, so make that absence explicit.
            root_compensation_required=False,
            root_compensation_supported=scenario.root_receipt.capabilities.supports_compensation,
            compensation_fails=scenario.compensation_fails,
            evidence_deadline_expired=scenario.evidence_deadline_expired,
            action_ids=tuple(action.descriptor.action_id for action in scenario.actions),
            required_invariants=scenario.required_invariants,
            fault_schedule=DevelopmentFaultSchedule.from_scenario(scenario),
        )


@dataclass(frozen=True)
class CommonArmResult:
    arm: str
    workflow_id: str
    logical_operation_id: str
    graph_sha256: str
    initial_status: str | None
    terminal_status: str
    duplicate_external_effect: bool
    recovery_work: int | None
    elapsed_ms: float
    evaluator: IndependentEvaluation | None
    comparable: bool
    limitation: str | None = None
    metrics: "CommonMetricTrace | None" = None


@dataclass(frozen=True)
class CommonMetricTrace:
    version: str
    logical_recovery_actions: int
    provider_submissions: int
    provider_verifications: int
    compensation_attempts: int
    retry_attempts: int
    duplicate_submissions: int
    semantic_validity_evaluations: int
    blocked_or_skipped_descendants: int
    actual_descendant_effects: int
    scheduler_or_replay_events: int


def run_effectguard_common_arm(
    scenario: DevelopmentScenario,
    specification: CommonWorkflowSpec,
    provider: LocalProviderClient,
) -> CommonArmResult:
    """Execute the real P4 runtime against a provider-owned observation trace."""

    started = perf_counter()
    acknowledgement, retry_attempts = _submit_with_retry(
        provider,
        logical_operation_id=specification.logical_operation_id,
        idempotency_key=specification.logical_operation_id,
        effect_class=scenario.root_receipt.effect_class,
        supports_compensation=scenario.root_receipt.capabilities.supports_compensation,
        acknowledge=False,
        retry_budget=specification.fault_schedule.retry_budget,
    )
    duplicate = False
    if specification.duplicate_submission:
        duplicate = provider.submit(
            logical_operation_id=specification.logical_operation_id,
            idempotency_key=specification.logical_operation_id,
            effect_class=scenario.root_receipt.effect_class,
            supports_compensation=scenario.root_receipt.capabilities.supports_compensation,
            acknowledge=False,
        ).duplicate
    initial_request = _request_for_observation(scenario, specification, acknowledgement.effect.observed_status, acknowledgement.effect.provider_reference)
    if scenario.resolved_status is not ObservedStatus.UNKNOWN:
        provider.resolve(specification.logical_operation_id, scenario.resolved_status)
    observed = provider.verify(specification.logical_operation_id)
    if observed is None:
        raise RuntimeError("shared local provider lost the submitted logical operation")
    final_request = _request_for_observation(scenario, specification, observed.observed_status, observed.provider_reference)
    runtime = UnknownSafeRecovery()
    initial_plan = runtime.plan(initial_request)
    final_plan = runtime.plan(final_request)
    outcome = runtime.execute(
        final_plan,
        lambda _step: not scenario.compensation_fails,
        lambda: FinalValidationResult(valid=not scenario.compensation_fails),
    )
    descendant_trace = _materialize_effectguard_descendants(scenario, specification, provider, final_plan)
    evaluation = IndependentEvaluator().evaluate(
        runtime_validity={certificate.action_id: certificate.result.value for certificate in final_plan.certificates},
        terminal_status=outcome.status.value,
        truth=IndependentTruth(
            expected_validity=scenario.expected_validity,
            invariants_hold=outcome.status is not RecoveryTerminalStatus.UNSAFE,
        ),
    )
    return CommonArmResult(
        arm="effectguard",
        workflow_id=specification.workflow_id,
        logical_operation_id=specification.logical_operation_id,
        graph_sha256=specification.graph_sha256,
        initial_status=initial_plan.terminal_status.value if initial_plan.terminal_status else None,
        terminal_status=outcome.status.value,
        duplicate_external_effect=duplicate,
        recovery_work=len(final_plan.recovery_steps) + len(descendant_trace),
        elapsed_ms=(perf_counter() - started) * 1000,
        evaluator=evaluation,
        comparable=True,
        metrics=CommonMetricTrace(
            "p4-common-metrics-v1",
            len(final_plan.recovery_steps),
            1 + int(duplicate) + sum(entry.endswith(":executed") for entry in descendant_trace),
            1 + sum(entry.endswith(":executed") for entry in descendant_trace),
            0,
            retry_attempts,
            int(duplicate),
            len(final_plan.certificates),
            sum(not entry.endswith(":executed") for entry in descendant_trace),
            sum(entry.endswith(":executed") for entry in descendant_trace),
            0,
        ),
    )


def _submit_with_retry(
    provider: LocalProviderClient,
    *,
    logical_operation_id: str,
    idempotency_key: str,
    effect_class: object,
    supports_compensation: bool,
    acknowledge: bool,
    retry_budget: int,
):
    """Retry only provider-declared transient failures; recovery policy is unchanged."""

    attempts = 0
    while True:
        try:
            return provider.submit(
                logical_operation_id=logical_operation_id,
                idempotency_key=idempotency_key,
                effect_class=effect_class,
                supports_compensation=supports_compensation,
                acknowledge=acknowledge,
            ), attempts
        except ProviderTransientError:
            if attempts >= retry_budget - 1:
                raise
            attempts += 1


def run_temporal_common_arm(
    specification: CommonWorkflowSpec,
    *,
    expected_validity: dict[str, str],
    temporal_service_address: str,
    provider_url: str,
    temporal_module: str | Path = "temporal-baseline",
) -> CommonArmResult:
    """Run a real Java Temporal workflow and parse its execution witness."""

    with TemporaryDirectory(prefix="effectguard-p4-common-temporal-") as temporary:
        witness = Path(temporary) / "temporal.properties"
        command = [
            "mvn",
            "-q",
            "-Dtest=ServiceBackedCommonWorkflowTest",
            f"-Dtemporal.service.address={temporal_service_address}",
            f"-Deffectguard.provider.url={provider_url}",
            f"-Deffectguard.common.workflow.id={specification.workflow_id}",
            f"-Deffectguard.common.operation.id={specification.logical_operation_id}",
            f"-Deffectguard.common.resolved_status={specification.resolved_status}",
            f"-Deffectguard.common.transient_failure=false",
            f"-Deffectguard.common.root_compensation_required={str(specification.root_compensation_required).lower()}",
            f"-Deffectguard.common.root_compensation_supported={str(specification.root_compensation_supported).lower()}",
            f"-Deffectguard.common.compensation_fails={str(specification.compensation_fails).lower()}",
            f"-Deffectguard.common.duplicate_submission={str(specification.duplicate_submission).lower()}",
            f"-Deffectguard.common.graph_sha256={specification.graph_sha256}",
            f"-Deffectguard.common.semantic_graph={specification.semantic_graph}",
            f"-Deffectguard.common.evidence_deadline_expired={str(specification.evidence_deadline_expired).lower()}",
            f"-Deffectguard.common.output={witness}",
            "test",
        ]
        started = perf_counter()
        subprocess.run(command, cwd=Path(temporal_module), check=True, capture_output=True, text=True)
        values = _read_properties(witness)
    runtime_validity = _parse_validity_summary(values.get("runtime_validity", ""))
    descendant_executions = values.get("descendant_trace", "").count("=executed")
    evaluation = IndependentEvaluator().evaluate(
        runtime_validity=runtime_validity,
        terminal_status=values["terminal_status"],
        truth=IndependentTruth(expected_validity=expected_validity, invariants_hold=True),
    )
    limitation = "Temporal materializes public descendants through the local provider; final evaluation remains development-only rather than sealed."
    return CommonArmResult(
        arm="temporal_service",
        workflow_id=values["workflow_id"],
        logical_operation_id=values["logical_operation_id"],
        graph_sha256=values["graph_sha256"],
        initial_status="BLOCKED",
        terminal_status=values["terminal_status"],
        duplicate_external_effect=values.get("duplicate_submission") == "true",
        recovery_work=int(values.get("recovery_work", values["activity_attempts"])),
        elapsed_ms=(perf_counter() - started) * 1000,
        evaluator=evaluation,
        comparable=False,
        limitation=limitation,
        metrics=CommonMetricTrace(
            "p4-common-metrics-v1",
            int(values.get("recovery_work", "0")),
            1 + int(values.get("duplicate_submission") == "true") + descendant_executions,
            1 + descendant_executions,
            int("explicitly compensated" in values.get("detail", "")),
            max(0, int(values["activity_attempts"]) - 1),
            int(values.get("duplicate_submission") == "true"),
            len(runtime_validity),
            sum(value != "VALID" for value in runtime_validity.values()),
            descendant_executions,
            int(values["activity_attempts"]),
        ),
    )


def _request_for_observation(
    scenario: DevelopmentScenario,
    specification: CommonWorkflowSpec,
    observed_status: ObservedStatus,
    provider_reference: str,
) -> RecoveryRequest:
    receipt = EffectReceipt(
        logical_operation_id=specification.logical_operation_id,
        effect_class=scenario.root_receipt.effect_class,
        observed_status=observed_status,
        provider_reference=provider_reference,
        idempotency_key=specification.logical_operation_id,
        capabilities=scenario.root_receipt.capabilities,
    )
    actions = tuple(
        action.descriptor.__class__(
            action_id=action.descriptor.action_id,
            logical_operation_id=action.descriptor.logical_operation_id,
            effect_class=action.descriptor.effect_class,
            requires_effects=tuple(
                specification.logical_operation_id if effect == scenario.root_receipt.logical_operation_id else effect
                for effect in action.descriptor.requires_effects
            ),
            conflicts_with_effects=tuple(
                specification.logical_operation_id if effect == scenario.root_receipt.logical_operation_id else effect
                for effect in action.descriptor.conflicts_with_effects
            ),
            capabilities=action.descriptor.capabilities,
        )
        for action in scenario.actions
    )
    return RecoveryRequest(
        workflow_id=specification.workflow_id,
        actions=actions,
        receipts=(receipt,),
        required_invariants=scenario.required_invariants,
        evidence_deadline_expired=specification.evidence_deadline_expired,
    )


def _materialize_effectguard_descendants(
    scenario: DevelopmentScenario,
    specification: CommonWorkflowSpec,
    provider: LocalProviderClient,
    plan: object,
) -> tuple[str, ...]:
    """Materialize only preserved actions; invalid or UNKNOWN actions remain unexecuted."""

    preserved = set(getattr(plan, "preserved_actions", ()))
    trace: list[str] = []
    for action in scenario.actions:
        if action.descriptor.action_id not in preserved:
            trace.append(f"{action.descriptor.action_id}:blocked_or_recovered")
            continue
        operation_id = f"{specification.logical_operation_id}:{action.descriptor.logical_operation_id}"
        acknowledgement = provider.submit(
            logical_operation_id=operation_id,
            idempotency_key=operation_id,
            effect_class=action.descriptor.effect_class,
            supports_compensation=action.descriptor.capabilities.supports_compensation,
            acknowledge=True,
        )
        provider.resolve(operation_id, ObservedStatus.SUCCESS)
        trace.append(f"{action.descriptor.action_id}:{'duplicate' if acknowledgement.duplicate else 'executed'}")
    return tuple(trace)


def _read_properties(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="latin-1").splitlines():
        if "=" in line and not line.startswith("#"):
            key, value = line.split("=", 1)
            values[key] = value.replace("\\:", ":").replace("\\=", "=").replace("\\\\", "\\")
    return values


def _parse_validity_summary(summary: str) -> dict[str, str]:
    return dict(item.split("=", 1) for item in summary.split(";") if "=" in item)


def _scenario(benchmark_path: Path, task_id: str) -> DevelopmentScenario:
    benchmark = load_development_benchmark(benchmark_path)
    return next(scenario for scenario in benchmark.scenarios if scenario.task_id == task_id)


def main(argv: Iterable[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run one development-only common EffectGuard/Temporal specification")
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--task-id")
    selection.add_argument("--all-development-scenarios", action="store_true")
    parser.add_argument("--pair-namespace", required=True)
    parser.add_argument("--benchmark", default="experiments/p4/development_benchmark_v1.json")
    parser.add_argument("--temporal-service-address")
    parser.add_argument("--effectguard-provider-url")
    parser.add_argument("--temporal-provider-url")
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args(argv)
    benchmark = load_development_benchmark(Path(arguments.benchmark))
    scenarios = benchmark.scenarios if arguments.all_development_scenarios else (_scenario(Path(arguments.benchmark), arguments.task_id),)
    payload = {"benchmark_id": benchmark.benchmark_id, "development_only": True, "runs": []}
    for scenario in scenarios:
        specification = CommonWorkflowSpec.from_scenario(scenario, pair_namespace=f"{arguments.pair_namespace}:{scenario.task_id}")
        run: dict[str, object] = {"specification": asdict(specification)}
        if arguments.effectguard_provider_url:
            run["effectguard"] = asdict(run_effectguard_common_arm(
                scenario,
                specification,
                LocalProviderClient(arguments.effectguard_provider_url),
            ))
        if arguments.temporal_service_address and arguments.temporal_provider_url:
            run["temporal"] = asdict(run_temporal_common_arm(
                specification,
                expected_validity=scenario.expected_validity,
                temporal_service_address=arguments.temporal_service_address,
                provider_url=arguments.temporal_provider_url,
            ))
        payload["runs"].append(run)
    rendered = json.dumps(payload, default=lambda value: asdict(value), sort_keys=True, indent=2)
    if arguments.output:
        arguments.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
