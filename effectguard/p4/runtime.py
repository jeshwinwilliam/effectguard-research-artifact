from __future__ import annotations

from typing import Callable, Protocol

from ..models import EffectClass, ObservedStatus, ValidityResult
from .models import (
    ActionDescriptor,
    EffectLedger,
    FinalValidationResult,
    RecoveryAuditRecord,
    RecoveryOutcome,
    RecoveryPlan,
    RecoveryRequest,
    RecoveryStep,
    RecoveryStepType,
    RecoveryTerminalStatus,
    ValidityCertificate,
)


class RuntimeValidityEstimator(Protocol):
    def evaluate(self, action: ActionDescriptor, request: RecoveryRequest) -> ValidityCertificate:
        """Estimate action validity from runtime-visible receipts only."""


class EvidenceValidityEstimator:
    """Small runtime estimator with no access to evaluator-only hidden truth."""

    def evaluate(self, action: ActionDescriptor, request: RecoveryRequest) -> ValidityCertificate:
        receipts = request.receipt_index()
        required = tuple(receipt_id for receipt_id in action.requires_effects if receipt_id in receipts)
        conflicts = tuple(receipt_id for receipt_id in action.conflicts_with_effects if receipt_id in receipts)
        evidence_ids = tuple(sorted(set(required + conflicts)))
        observed = {receipt_id: receipts[receipt_id].observed_status for receipt_id in evidence_ids}

        if any(status is ObservedStatus.UNKNOWN for status in observed.values()):
            return ValidityCertificate(
                action.action_id,
                ValidityResult.UNKNOWN,
                evidence_ids,
                "required or conflicting external effect remains UNKNOWN",
            )
        if any(observed[receipt_id] is ObservedStatus.FAILURE for receipt_id in required):
            return ValidityCertificate(
                action.action_id,
                ValidityResult.INVALID,
                evidence_ids,
                "required external effect is confirmed failed",
            )
        if any(observed[receipt_id] is ObservedStatus.SUCCESS for receipt_id in conflicts):
            return ValidityCertificate(
                action.action_id,
                ValidityResult.INVALID,
                evidence_ids,
                "confirmed external effect conflicts with this action",
            )
        return ValidityCertificate(action.action_id, ValidityResult.VALID, evidence_ids, "runtime evidence is consistent")


class UnknownSafeRecovery:
    def __init__(self, estimator: RuntimeValidityEstimator | None = None) -> None:
        self._estimator = estimator or EvidenceValidityEstimator()

    def plan(self, request: RecoveryRequest) -> RecoveryPlan:
        certificates = tuple(self._estimator.evaluate(action, request) for action in request.actions)
        action_index = {action.action_id: action for action in request.actions}
        valid = tuple(certificate.action_id for certificate in certificates if certificate.result is ValidityResult.VALID)
        unknown = tuple(certificate.action_id for certificate in certificates if certificate.result is ValidityResult.UNKNOWN)
        invalid = tuple(certificate.action_id for certificate in certificates if certificate.result is ValidityResult.INVALID)
        audit_records = [
            RecoveryAuditRecord(
                "validity_estimated",
                certificate.action_id,
                certificate.evidence_ids,
                f"{certificate.result.value}: {certificate.reason}",
            )
            for certificate in certificates
        ]

        unknown_irreversible = tuple(
            action_id
            for action_id in unknown
            if action_index[action_id].effect_class is EffectClass.IRREVERSIBLE
        )
        if unknown:
            status = RecoveryTerminalStatus.UNRESOLVED if request.evidence_deadline_expired else RecoveryTerminalStatus.BLOCKED
            detail = "evidence deadline expired" if request.evidence_deadline_expired else "waiting for decisive external evidence"
            if unknown_irreversible:
                detail = f"{detail}; irreversible actions remain in the UNKNOWN conflict cone"
            audit_records.append(RecoveryAuditRecord("unknown_barrier", None, unknown, detail))
            return RecoveryPlan(
                workflow_id=request.workflow_id,
                certificates=certificates,
                preserved_actions=valid,
                deferred_actions=unknown,
                invalid_actions=invalid,
                recovery_steps=(),
                terminal_status=status,
                audit_records=tuple(audit_records),
            )

        unsupported = tuple(
            action_id
            for action_id in invalid
            if action_index[action_id].effect_class is EffectClass.IRREVERSIBLE
            or not action_index[action_id].capabilities.supports_compensation
            and action_index[action_id].effect_class in {EffectClass.REVERSIBLE, EffectClass.COMPENSABLE}
        )
        if unsupported:
            audit_records.append(
                RecoveryAuditRecord(
                    "recovery_unsupported",
                    unsupported[0],
                    (),
                    "invalid effect cannot be safely reversed with declared provider capabilities",
                )
            )
            return RecoveryPlan(
                workflow_id=request.workflow_id,
                certificates=certificates,
                preserved_actions=valid,
                deferred_actions=(),
                invalid_actions=invalid,
                recovery_steps=(),
                terminal_status=RecoveryTerminalStatus.RECOVERY_UNSUPPORTED,
                audit_records=tuple(audit_records),
            )

        steps: list[RecoveryStep] = []
        for action_id in invalid:
            action = action_index[action_id]
            if action.effect_class in {EffectClass.READ, EffectClass.PURE}:
                steps.append(RecoveryStep(action_id, RecoveryStepType.RECOMPUTE, "invalid read or pure result must be recomputed"))
            else:
                steps.append(RecoveryStep(action_id, RecoveryStepType.COMPENSATE, "invalid external effect must be compensated"))
                steps.append(RecoveryStep(action_id, RecoveryStepType.REEXECUTE, "corrected external effect must be reexecuted"))
        return RecoveryPlan(
            workflow_id=request.workflow_id,
            certificates=certificates,
            preserved_actions=valid,
            deferred_actions=(),
            invalid_actions=invalid,
            recovery_steps=tuple(steps),
            terminal_status=None,
            audit_records=tuple(audit_records),
        )

    def can_start(self, action: ActionDescriptor, request: RecoveryRequest, ledger: EffectLedger) -> RecoveryAuditRecord:
        certificate = self._estimator.evaluate(action, request)
        if certificate.result is ValidityResult.UNKNOWN:
            return RecoveryAuditRecord("action_blocked", action.action_id, certificate.evidence_ids, "UNKNOWN evidence prevents action start")
        if action.effect_class is EffectClass.IRREVERSIBLE and certificate.result is ValidityResult.INVALID:
            return RecoveryAuditRecord("action_rejected", action.action_id, certificate.evidence_ids, "invalid irreversible action cannot start")
        existing = ledger._submitted.get(action.logical_operation_id)
        if existing is not None:
            decision = ledger.register_submission(existing)
            return RecoveryAuditRecord("action_blocked", action.action_id, (action.logical_operation_id,), decision.reason)
        return RecoveryAuditRecord("action_permitted", action.action_id, certificate.evidence_ids, "action has decisive safe evidence")

    def execute(
        self,
        plan: RecoveryPlan,
        execute_step: Callable[[RecoveryStep], bool],
        validate_final_state: Callable[[], FinalValidationResult],
    ) -> RecoveryOutcome:
        audit_records = list(plan.audit_records)
        if plan.terminal_status is not None:
            return RecoveryOutcome(plan.terminal_status, plan, None, tuple(audit_records))
        for step in plan.recovery_steps:
            succeeded = execute_step(step)
            audit_records.append(
                RecoveryAuditRecord(
                    "recovery_step_completed" if succeeded else "recovery_step_failed",
                    step.action_id,
                    (),
                    step.step_type.value,
                )
            )
            if not succeeded:
                return RecoveryOutcome(RecoveryTerminalStatus.FAILED, plan, None, tuple(audit_records))
        validation = validate_final_state()
        if not validation.valid:
            audit_records.append(
                RecoveryAuditRecord("final_invariant_failed", None, validation.violated_invariants, "recovery cannot be reported as successful")
            )
            return RecoveryOutcome(RecoveryTerminalStatus.UNSAFE, plan, validation, tuple(audit_records))
        audit_records.append(RecoveryAuditRecord("final_invariant_validated", None, (), "all required invariants hold"))
        return RecoveryOutcome(RecoveryTerminalStatus.RECOVERED, plan, validation, tuple(audit_records))
