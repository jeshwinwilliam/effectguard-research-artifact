"""Development-only paired policy harness using the local external-effect provider.

This module compares policy planners over the same provider materialization.
It does not launch Temporal itself: service-backed Temporal tests remain a
separate opt-in integration check. The Temporal arm here models the application
policy that the Java workflow must use with the same public contract.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory

from ..models import ObservedStatus
from .benchmark import DevelopmentScenario
from .local_provider import LocalEffectProvider
from .models import EffectReceipt, FinalValidationResult, RecoveryOutcome, RecoveryPlan, RecoveryRequest, RecoveryStepType, RecoveryTerminalStatus
from .retro_inspired import RetroInspiredSemanticRecovery
from .runtime import UnknownSafeRecovery
from .temporal_policy import TemporalApplicationUnknownPolicy


@dataclass(frozen=True)
class PairedPolicyResult:
    policy: str
    initial_status: RecoveryTerminalStatus | None
    final_status: RecoveryTerminalStatus
    selected_actions: tuple[str, ...]
    preserved_actions: tuple[str, ...]
    recovery_step_count: int
    actual_invariants_hold: bool
    trace: tuple[str, ...]


@dataclass(frozen=True)
class PairedDevelopmentResult:
    task_id: str
    public_context_sha256: str
    initial_observation: ObservedStatus
    resolved_observation: ObservedStatus
    effectguard: PairedPolicyResult
    temporal_application: PairedPolicyResult
    retro_inspired: PairedPolicyResult


def run_paired_development_scenario(scenario: DevelopmentScenario) -> PairedDevelopmentResult:
    """Run all policy arms against one provider-owned public observation trace."""

    with TemporaryDirectory(prefix="effectguard-p4-paired-") as temporary:
        initial_request, resolved_request = _materialize_public_requests(scenario, Path(temporary) / "provider.sqlite")
    context_sha = _public_context_sha256(resolved_request)
    effectguard_runtime = UnknownSafeRecovery()
    policies = (
        ("effectguard", effectguard_runtime.plan(initial_request), effectguard_runtime.plan(resolved_request)),
        ("temporal_application", TemporalApplicationUnknownPolicy().plan(initial_request), TemporalApplicationUnknownPolicy().plan(resolved_request)),
        ("retro_inspired", RetroInspiredSemanticRecovery().plan(initial_request), RetroInspiredSemanticRecovery().plan(resolved_request)),
    )
    results = {
        name: _result_for_policy(name, initial_plan, final_plan, scenario)
        for name, initial_plan, final_plan in policies
    }
    return PairedDevelopmentResult(
        task_id=scenario.task_id,
        public_context_sha256=context_sha,
        initial_observation=initial_request.receipts[0].observed_status,
        resolved_observation=resolved_request.receipts[0].observed_status,
        effectguard=results["effectguard"],
        temporal_application=results["temporal_application"],
        retro_inspired=results["retro_inspired"],
    )


def _materialize_public_requests(scenario: DevelopmentScenario, database: Path) -> tuple[RecoveryRequest, RecoveryRequest]:
    provider = LocalEffectProvider(database)
    try:
        acknowledgement = provider.submit(
            logical_operation_id=scenario.root_receipt.logical_operation_id,
            idempotency_key=scenario.root_receipt.idempotency_key or scenario.root_receipt.logical_operation_id,
            effect_class=scenario.root_receipt.effect_class,
            supports_compensation=scenario.root_receipt.capabilities.supports_compensation,
            acknowledge=False,
        )
        initial = _request_with_receipt(scenario, acknowledgement.effect.observed_status, acknowledgement.effect.provider_reference)
        provider.resolve(scenario.root_receipt.logical_operation_id, scenario.resolved_status)
        resolved_effect = provider.verify_required(scenario.root_receipt.logical_operation_id)
        resolved = _request_with_receipt(scenario, resolved_effect.observed_status, resolved_effect.provider_reference)
        return initial, resolved
    finally:
        provider.close()


def _request_with_receipt(scenario: DevelopmentScenario, observed_status: ObservedStatus, provider_reference: str) -> RecoveryRequest:
    receipt = EffectReceipt(
        logical_operation_id=scenario.root_receipt.logical_operation_id,
        effect_class=scenario.root_receipt.effect_class,
        observed_status=observed_status,
        provider_reference=provider_reference,
        idempotency_key=scenario.root_receipt.idempotency_key,
        capabilities=scenario.root_receipt.capabilities,
    )
    return RecoveryRequest(
        workflow_id=scenario.task_id,
        actions=tuple(action.descriptor for action in scenario.actions),
        receipts=(receipt,),
        required_invariants=scenario.required_invariants,
        evidence_deadline_expired=scenario.evidence_deadline_expired,
    )


def _public_context_sha256(request: RecoveryRequest) -> str:
    payload = "|".join(
        [
            request.workflow_id,
            *(
                f"{receipt.logical_operation_id}:{receipt.observed_status.value}:{receipt.idempotency_key}:{receipt.provider_reference}"
                for receipt in request.receipts
            ),
            *(f"{action.action_id}:{action.logical_operation_id}:{action.effect_class.value}" for action in request.actions),
            *request.required_invariants,
        ]
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _result_for_policy(
    policy: str,
    initial_plan: RecoveryPlan,
    final_plan: RecoveryPlan,
    scenario: DevelopmentScenario,
) -> PairedPolicyResult:
    outcome = _execute_development_plan(final_plan, scenario)
    return PairedPolicyResult(
        policy=policy,
        initial_status=initial_plan.terminal_status,
        final_status=outcome.status,
        selected_actions=final_plan.invalid_actions,
        preserved_actions=final_plan.preserved_actions,
        recovery_step_count=len(final_plan.recovery_steps),
        actual_invariants_hold=(
            bool(outcome.final_validation and outcome.final_validation.valid)
            if outcome.final_validation is not None
            else outcome.status
            in {
                RecoveryTerminalStatus.BLOCKED,
                RecoveryTerminalStatus.UNRESOLVED,
                RecoveryTerminalStatus.RECOVERY_UNSUPPORTED,
            }
        ),
        trace=tuple(record.event for record in outcome.audit_records),
    )


def _execute_development_plan(plan: RecoveryPlan, scenario: DevelopmentScenario) -> RecoveryOutcome:
    if plan.terminal_status is not None:
        return RecoveryOutcome(plan.terminal_status, plan, None, plan.audit_records)
    for step in plan.recovery_steps:
        if step.step_type is RecoveryStepType.COMPENSATE and scenario.compensation_fails:
            return RecoveryOutcome(RecoveryTerminalStatus.FAILED, plan, None, plan.audit_records)
    validation = FinalValidationResult(valid=True)
    return RecoveryOutcome(RecoveryTerminalStatus.RECOVERED, plan, validation, plan.audit_records)
