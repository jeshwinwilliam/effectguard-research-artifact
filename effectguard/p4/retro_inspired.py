"""Development-only semantic recovery policy inspired by RETRO.

This is not RETRO and does not reproduce its Linux action-history machinery.
It makes the comparison policy explicit: semantic equivalence over runtime
receipts selectively preserves actions, while unresolved external effects pause
or escalate instead of being optimistically replayed.
"""

from __future__ import annotations

from ..models import EffectClass, ObservedStatus, ValidityResult
from .models import (
    ActionDescriptor,
    RecoveryAuditRecord,
    RecoveryPlan,
    RecoveryRequest,
    RecoveryStep,
    RecoveryStepType,
    RecoveryTerminalStatus,
    ValidityCertificate,
)


class RetroInspiredSemanticRecovery:
    """A capability-matched semantic baseline for development workloads only."""

    def plan(self, request: RecoveryRequest) -> RecoveryPlan:
        certificates = tuple(self._equivalence_certificate(action, request) for action in request.actions)
        actions = {action.action_id: action for action in request.actions}
        valid = tuple(c.action_id for c in certificates if c.result is ValidityResult.VALID)
        unknown = tuple(c.action_id for c in certificates if c.result is ValidityResult.UNKNOWN)
        invalid = tuple(c.action_id for c in certificates if c.result is ValidityResult.INVALID)
        audit = [
            RecoveryAuditRecord(
                "retro_semantic_equivalence",
                certificate.action_id,
                certificate.evidence_ids,
                f"{certificate.result.value}: {certificate.reason}",
            )
            for certificate in certificates
        ]

        if unknown:
            terminal = RecoveryTerminalStatus.UNRESOLVED if request.evidence_deadline_expired else RecoveryTerminalStatus.BLOCKED
            detail = "semantic recovery paused because public external evidence remains unresolved"
            audit.append(RecoveryAuditRecord("retro_pause_or_escalate", None, unknown, detail))
            return RecoveryPlan(request.workflow_id, certificates, valid, unknown, invalid, (), terminal, tuple(audit))

        unsupported = tuple(
            action_id
            for action_id in invalid
            if actions[action_id].effect_class is EffectClass.IRREVERSIBLE
            or (
                actions[action_id].effect_class in {EffectClass.REVERSIBLE, EffectClass.COMPENSABLE}
                and not actions[action_id].capabilities.supports_compensation
            )
        )
        if unsupported:
            audit.append(
                RecoveryAuditRecord(
                    "retro_escalation_required",
                    unsupported[0],
                    (),
                    "semantic recovery cannot safely compensate the invalid external effect",
                )
            )
            return RecoveryPlan(
                request.workflow_id,
                certificates,
                valid,
                (),
                invalid,
                (),
                RecoveryTerminalStatus.RECOVERY_UNSUPPORTED,
                tuple(audit),
            )

        steps: list[RecoveryStep] = []
        for action_id in invalid:
            action = actions[action_id]
            if action.effect_class in {EffectClass.READ, EffectClass.PURE}:
                steps.append(RecoveryStep(action_id, RecoveryStepType.RECOMPUTE, "semantic input changed"))
            else:
                steps.append(RecoveryStep(action_id, RecoveryStepType.COMPENSATE, "invalid external effect requires compensation"))
                steps.append(RecoveryStep(action_id, RecoveryStepType.REEXECUTE, "re-execute after semantic repair"))
        return RecoveryPlan(request.workflow_id, certificates, valid, (), invalid, tuple(steps), None, tuple(audit))

    @staticmethod
    def _equivalence_certificate(action: ActionDescriptor, request: RecoveryRequest) -> ValidityCertificate:
        receipts = request.receipt_index()
        required = tuple(receipt_id for receipt_id in action.requires_effects if receipt_id in receipts)
        conflicts = tuple(receipt_id for receipt_id in action.conflicts_with_effects if receipt_id in receipts)
        evidence_ids = tuple(sorted(set(required + conflicts)))
        observed = {effect_id: receipts[effect_id].observed_status for effect_id in evidence_ids}
        if any(value is ObservedStatus.UNKNOWN for value in observed.values()):
            return ValidityCertificate(action.action_id, ValidityResult.UNKNOWN, evidence_ids, "semantic inputs cannot be compared yet")
        if any(observed[effect_id] is ObservedStatus.FAILURE for effect_id in required):
            return ValidityCertificate(action.action_id, ValidityResult.INVALID, evidence_ids, "required semantic input changed to failure")
        if any(observed[effect_id] is ObservedStatus.SUCCESS for effect_id in conflicts):
            return ValidityCertificate(action.action_id, ValidityResult.INVALID, evidence_ids, "conflicting semantic input is present")
        return ValidityCertificate(action.action_id, ValidityResult.VALID, evidence_ids, "public semantic inputs remain equivalent")
