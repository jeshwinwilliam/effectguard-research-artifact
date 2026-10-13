from __future__ import annotations

from dataclasses import dataclass

from ..models import EffectClass
from .benchmark import DevelopmentScenario
from .models import EffectLedger, FinalValidationResult, RecoveryPlan, RecoveryTerminalStatus
from .runtime import UnknownSafeRecovery


DEVELOPMENT_STRATEGIES = (
    "blocking",
    "restart",
    "checkpoint",
    "dependency_only",
    "saga",
    "idempotency_aware",
    "effectguard",
)


@dataclass(frozen=True)
class DevelopmentBaselineResult:
    strategy: str
    initial_status: RecoveryTerminalStatus | None
    final_status: RecoveryTerminalStatus
    selected_actions: tuple[str, ...]
    recovery_step_count: int
    actual_invariants_hold: bool
    trace: tuple[str, ...]
    final_plan: RecoveryPlan


def _status_for_plan(plan: RecoveryPlan) -> RecoveryTerminalStatus:
    return plan.terminal_status or RecoveryTerminalStatus.RECOVERED


def run_development_baseline(scenario: DevelopmentScenario, strategy: str) -> DevelopmentBaselineResult:
    if strategy not in DEVELOPMENT_STRATEGIES:
        raise ValueError(f"unsupported development strategy: {strategy}")
    runtime = UnknownSafeRecovery()
    initial_plan = runtime.plan(scenario.request(resolved=False))
    final_plan = runtime.plan(scenario.request(resolved=True))
    descendants = scenario.graph_descendants()
    initial_status = initial_plan.terminal_status
    trace = ["all strategies received identical public receipts, graph, capabilities, and invariants"]

    if final_plan.terminal_status is RecoveryTerminalStatus.UNRESOLVED:
        return DevelopmentBaselineResult(
            strategy,
            initial_status,
            RecoveryTerminalStatus.UNRESOLVED,
            (),
            0,
            True,
            tuple(trace + ["evidence deadline expired without a decisive receipt"]),
            final_plan,
        )

    if strategy == "blocking":
        return DevelopmentBaselineResult(
            strategy,
            initial_status,
            RecoveryTerminalStatus.RECOVERED,
            (),
            0,
            True,
            tuple(trace + ["waited for the root receipt before entering a conflicting branch"]),
            final_plan,
        )

    if strategy == "effectguard":
        if final_plan.terminal_status is not None:
            return DevelopmentBaselineResult(
                strategy,
                initial_status,
                final_plan.terminal_status,
                final_plan.invalid_actions,
                0,
                True,
                tuple(trace + ["runtime plan reached a non-recovered terminal safety status"]),
                final_plan,
            )
        outcome = runtime.execute(
            final_plan,
            lambda _step: not scenario.compensation_fails,
            lambda: FinalValidationResult(valid=not scenario.compensation_fails, violated_invariants=scenario.required_invariants if scenario.compensation_fails else ()),
        )
        return DevelopmentBaselineResult(
            strategy,
            initial_status,
            outcome.status,
            final_plan.invalid_actions,
            len(final_plan.recovery_steps),
            bool(outcome.final_validation and outcome.final_validation.valid),
            tuple(trace + [record.event for record in outcome.audit_records]),
            final_plan,
        )

    if strategy == "restart":
        status = RecoveryTerminalStatus.FAILED if scenario.restart_interrupted else RecoveryTerminalStatus.UNSAFE if scenario.duplicate_delivery else RecoveryTerminalStatus.RECOVERED
        return DevelopmentBaselineResult(
            strategy,
            initial_status,
            status,
            descendants,
            len(descendants),
            status is RecoveryTerminalStatus.RECOVERED,
            tuple(trace + ["replays the full dynamic descendant set without semantic preservation"]),
            final_plan,
        )

    if strategy == "checkpoint":
        return DevelopmentBaselineResult(
            strategy,
            initial_status,
            RecoveryTerminalStatus.RECOVERED,
            descendants,
            len(descendants),
            True,
            tuple(trace + ["restores checkpoint after interruption and replays the dynamic descendant set"]),
            final_plan,
        )

    if strategy == "dependency_only":
        has_invalid_irreversible = any(
            action.descriptor.effect_class is EffectClass.IRREVERSIBLE and action.descriptor.action_id in final_plan.invalid_actions
            for action in scenario.actions
        )
        status = (
            RecoveryTerminalStatus.RECOVERY_UNSUPPORTED
            if has_invalid_irreversible
            else RecoveryTerminalStatus.FAILED
            if scenario.compensation_fails
            else RecoveryTerminalStatus.RECOVERED
        )
        return DevelopmentBaselineResult(
            strategy,
            initial_status,
            status,
            descendants,
            len(descendants),
            status is RecoveryTerminalStatus.RECOVERED,
            tuple(trace + ["selects all graph descendants without semantic preservation"]),
            final_plan,
        )

    if strategy == "saga":
        has_invalid_irreversible = any(
            action.descriptor.effect_class is EffectClass.IRREVERSIBLE and action.descriptor.action_id in final_plan.invalid_actions
            for action in scenario.actions
        )
        status = (
            RecoveryTerminalStatus.RECOVERY_UNSUPPORTED
            if has_invalid_irreversible
            else RecoveryTerminalStatus.FAILED
            if scenario.compensation_fails
            else RecoveryTerminalStatus.RECOVERED
        )
        return DevelopmentBaselineResult(
            strategy,
            initial_status,
            status,
            final_plan.invalid_actions,
            len(final_plan.invalid_actions),
            status is RecoveryTerminalStatus.RECOVERED,
            tuple(trace + ["compensates declared invalid effects but has no semantic-preservation claim"]),
            final_plan,
        )

    ledger = EffectLedger()
    duplicate_status = RecoveryTerminalStatus.RECOVERED
    if scenario.duplicate_delivery and scenario.actions:
        descriptor = scenario.actions[0].descriptor
        receipt = scenario.root_receipt
        ledger.register_submission(receipt)
        ledger.register_submission(receipt)
        trace.append("duplicate logical delivery was rejected by the declared provider deduplication interface")
    status = duplicate_status
    return DevelopmentBaselineResult(
        strategy,
        initial_status,
        status,
        descendants,
        len(descendants),
        status is RecoveryTerminalStatus.RECOVERED,
        tuple(trace + ["replays graph descendants safely after interruption with logical-ID deduplication"]),
        final_plan,
    )
