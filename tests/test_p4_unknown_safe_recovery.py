from __future__ import annotations

import pytest

from effectguard.models import EffectClass, ObservedStatus
from effectguard.p4 import (
    ActionDescriptor,
    EffectLedger,
    EffectReceipt,
    FinalValidationResult,
    ProviderCapabilities,
    RecoveryRequest,
    RecoveryTerminalStatus,
    UnknownSafeRecovery,
)


IDEMPOTENT = ProviderCapabilities(
    supports_idempotency=True,
    supports_deduplication_lookup=True,
    supports_verification=True,
    supports_compensation=True,
)


def _receipt(status: ObservedStatus) -> EffectReceipt:
    return EffectReceipt(
        logical_operation_id="capacity-a",
        effect_class=EffectClass.READ,
        observed_status=status,
        provider_reference="capacity-a-receipt",
        idempotency_key="capacity-a-key",
        capabilities=IDEMPOTENT,
    )


def _action(*, action_id: str, effect_class: EffectClass, conflicts: tuple[str, ...] = (), capabilities: ProviderCapabilities = IDEMPOTENT) -> ActionDescriptor:
    return ActionDescriptor(
        action_id=action_id,
        logical_operation_id=f"logical-{action_id}",
        effect_class=effect_class,
        conflicts_with_effects=conflicts,
        capabilities=capabilities,
    )


def _request(receipt_status: ObservedStatus, *actions: ActionDescriptor, evidence_deadline_expired: bool = False) -> RecoveryRequest:
    return RecoveryRequest(
        workflow_id="p4-s9",
        actions=tuple(actions),
        receipts=(_receipt(receipt_status),),
        required_invariants=("exactly one submitted job",),
        evidence_deadline_expired=evidence_deadline_expired,
    )


def test_delayed_success_blocks_conflicting_irreversible_action_but_preserves_independent_work() -> None:
    runtime = UnknownSafeRecovery()
    tax = _action(action_id="tax", effect_class=EffectClass.PURE)
    submit_b = _action(action_id="submit-b", effect_class=EffectClass.IRREVERSIBLE, conflicts=("capacity-a",))

    plan = runtime.plan(_request(ObservedStatus.UNKNOWN, tax, submit_b))

    assert plan.terminal_status is RecoveryTerminalStatus.BLOCKED
    assert plan.preserved_actions == ("tax",)
    assert plan.deferred_actions == ("submit-b",)
    assert "submit-b" not in plan.preserved_actions

    resolved_plan = runtime.plan(_request(ObservedStatus.SUCCESS, tax, submit_b))
    assert resolved_plan.terminal_status is RecoveryTerminalStatus.RECOVERY_UNSUPPORTED
    assert resolved_plan.invalid_actions == ("submit-b",)


def test_delayed_failure_allows_safe_fallback_after_evidence_resolves() -> None:
    runtime = UnknownSafeRecovery()
    submit_b = _action(action_id="submit-b", effect_class=EffectClass.IRREVERSIBLE, conflicts=("capacity-a",))

    plan = runtime.plan(_request(ObservedStatus.FAILURE, submit_b))
    outcome = runtime.execute(plan, lambda _step: True, lambda: FinalValidationResult(valid=True))

    assert plan.terminal_status is None
    assert plan.preserved_actions == ("submit-b",)
    assert outcome.status is RecoveryTerminalStatus.RECOVERED


def test_evidence_deadline_marks_unknown_state_unresolved() -> None:
    runtime = UnknownSafeRecovery()
    submit_b = _action(action_id="submit-b", effect_class=EffectClass.IRREVERSIBLE, conflicts=("capacity-a",))

    plan = runtime.plan(_request(ObservedStatus.UNKNOWN, submit_b, evidence_deadline_expired=True))

    assert plan.terminal_status is RecoveryTerminalStatus.UNRESOLVED


def test_duplicate_logical_submission_is_rejected_when_deduplication_is_available() -> None:
    ledger = EffectLedger()
    receipt = _receipt(ObservedStatus.SUCCESS)

    assert ledger.register_submission(receipt).accepted is True
    decision = ledger.register_submission(receipt)

    assert decision.accepted is False
    assert decision.terminal_status is RecoveryTerminalStatus.BLOCKED


def test_duplicate_logical_submission_without_provider_deduplication_is_unsupported() -> None:
    ledger = EffectLedger()
    unsupported = ProviderCapabilities(supports_idempotency=False, supports_deduplication_lookup=False)
    receipt = EffectReceipt(
        logical_operation_id="job-b",
        effect_class=EffectClass.IRREVERSIBLE,
        observed_status=ObservedStatus.SUCCESS,
        provider_reference="job-b-receipt",
        idempotency_key=None,
        capabilities=unsupported,
    )

    assert ledger.register_submission(receipt).accepted is True
    decision = ledger.register_submission(receipt)

    assert decision.terminal_status is RecoveryTerminalStatus.RECOVERY_UNSUPPORTED


def test_compensation_failure_cannot_report_recovered() -> None:
    runtime = UnknownSafeRecovery()
    reserve_b = _action(action_id="reserve-b", effect_class=EffectClass.COMPENSABLE, conflicts=("capacity-a",))

    plan = runtime.plan(_request(ObservedStatus.SUCCESS, reserve_b))
    outcome = runtime.execute(plan, lambda _step: False, lambda: FinalValidationResult(valid=True))

    assert plan.recovery_steps
    assert outcome.status is RecoveryTerminalStatus.FAILED


def test_final_invariant_failure_overrides_successful_recovery_steps() -> None:
    runtime = UnknownSafeRecovery()
    tax = _action(action_id="tax", effect_class=EffectClass.PURE)
    plan = runtime.plan(_request(ObservedStatus.SUCCESS, tax))

    outcome = runtime.execute(
        plan,
        lambda _step: True,
        lambda: FinalValidationResult(valid=False, violated_invariants=("exactly one submitted job",)),
    )

    assert outcome.status is RecoveryTerminalStatus.UNSAFE
    assert outcome.final_validation is not None
    assert outcome.final_validation.violated_invariants == ("exactly one submitted job",)


def test_invalid_irreversible_effect_is_rejected_as_unsupported() -> None:
    runtime = UnknownSafeRecovery()
    submit_b = _action(action_id="submit-b", effect_class=EffectClass.IRREVERSIBLE, conflicts=("capacity-a",))

    plan = runtime.plan(_request(ObservedStatus.SUCCESS, submit_b))

    assert plan.terminal_status is RecoveryTerminalStatus.RECOVERY_UNSUPPORTED


def test_can_start_blocks_unknown_action_before_external_submission() -> None:
    runtime = UnknownSafeRecovery()
    ledger = EffectLedger()
    submit_b = _action(action_id="submit-b", effect_class=EffectClass.IRREVERSIBLE, conflicts=("capacity-a",))

    decision = runtime.can_start(submit_b, _request(ObservedStatus.UNKNOWN, submit_b), ledger)

    assert decision.event == "action_blocked"
    assert "UNKNOWN" in decision.detail


def test_logical_operation_identifier_is_required() -> None:
    with pytest.raises(ValueError, match="logical operation identifier"):
        ActionDescriptor(action_id="missing-id", logical_operation_id="", effect_class=EffectClass.PURE)
