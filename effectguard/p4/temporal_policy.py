"""Capability-matched Temporal application policy for development pairing.

The class models policy code that belongs in a Temporal Workflow/Activity
application. It is deliberately separate from Temporal's native replay and
from EffectGuard's runtime so that policy, not platform features, is compared.
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


class TemporalApplicationUnknownPolicy:
    """Application-defined UNKNOWN policy with the same public capabilities."""

    def plan(self, request: RecoveryRequest) -> RecoveryPlan:
        certificates = tuple(self._classify(action, request) for action in request.actions)
        actions = {action.action_id: action for action in request.actions}
        valid = tuple(c.action_id for c in certificates if c.result is ValidityResult.VALID)
        unknown = tuple(c.action_id for c in certificates if c.result is ValidityResult.UNKNOWN)
        invalid = tuple(c.action_id for c in certificates if c.result is ValidityResult.INVALID)
        audit = [
            RecoveryAuditRecord(
                "temporal_application_validity",
                certificate.action_id,
                certificate.evidence_ids,
                f"{certificate.result.value}: {certificate.reason}",
            )
            for certificate in certificates
        ]

        if unknown:
            terminal = RecoveryTerminalStatus.UNRESOLVED if request.evidence_deadline_expired else RecoveryTerminalStatus.BLOCKED
            audit.append(RecoveryAuditRecord("temporal_application_wait", None, unknown, "workflow waits for verification or reaches evidence deadline"))
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
            audit.append(RecoveryAuditRecord("temporal_application_unsupported", unsupported[0], (), "required compensation capability is unavailable"))
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
                steps.append(RecoveryStep(action_id, RecoveryStepType.RECOMPUTE, "application predicate marked input invalid"))
            else:
                steps.append(RecoveryStep(action_id, RecoveryStepType.COMPENSATE, "application policy compensates invalid effect"))
                steps.append(RecoveryStep(action_id, RecoveryStepType.REEXECUTE, "application policy re-executes corrected effect"))
        return RecoveryPlan(request.workflow_id, certificates, valid, (), invalid, tuple(steps), None, tuple(audit))

    @staticmethod
    def _classify(action: ActionDescriptor, request: RecoveryRequest) -> ValidityCertificate:
        receipts = request.receipt_index()
        required = tuple(effect_id for effect_id in action.requires_effects if effect_id in receipts)
        conflicts = tuple(effect_id for effect_id in action.conflicts_with_effects if effect_id in receipts)
        evidence_ids = tuple(sorted(set(required + conflicts)))
        observed = {effect_id: receipts[effect_id].observed_status for effect_id in evidence_ids}
        if any(value is ObservedStatus.UNKNOWN for value in observed.values()):
            return ValidityCertificate(action.action_id, ValidityResult.UNKNOWN, evidence_ids, "Temporal application awaits decisive provider verification")
        if any(observed[effect_id] is ObservedStatus.FAILURE for effect_id in required):
            return ValidityCertificate(action.action_id, ValidityResult.INVALID, evidence_ids, "required provider effect is confirmed failed")
        if any(observed[effect_id] is ObservedStatus.SUCCESS for effect_id in conflicts):
            return ValidityCertificate(action.action_id, ValidityResult.INVALID, evidence_ids, "provider effect conflicts with this action")
        return ValidityCertificate(action.action_id, ValidityResult.VALID, evidence_ids, "Temporal application observes semantically valid inputs")
