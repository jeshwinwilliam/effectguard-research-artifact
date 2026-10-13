from __future__ import annotations

from dataclasses import dataclass

from ..models import RecoveryStatus
from .models import RecoveryOutcome, RecoveryPlan, RecoveryTerminalStatus


def adapt_p1_terminal_status(status: RecoveryStatus, *, final_state_correct: bool) -> RecoveryTerminalStatus:
    """Translate P1 outcomes to P4 terminal semantics without claiming executor equivalence."""

    if status in {RecoveryStatus.RECOVERED, RecoveryStatus.NOT_NEEDED}:
        return RecoveryTerminalStatus.RECOVERED if final_state_correct else RecoveryTerminalStatus.UNSAFE
    if status is RecoveryStatus.RECOVERY_UNSUPPORTED:
        return RecoveryTerminalStatus.RECOVERY_UNSUPPORTED
    if status is RecoveryStatus.RECOVERY_UNSAFE:
        return RecoveryTerminalStatus.UNSAFE
    if status is RecoveryStatus.RECOVERY_FAILED:
        return RecoveryTerminalStatus.FAILED
    raise ValueError(f"unsupported P1 recovery status: {status}")


@dataclass(frozen=True)
class RecoveryBehavior:
    selected_actions: frozenset[str]
    preserved_actions: frozenset[str]
    compensation_actions: frozenset[str]
    terminal_status: RecoveryTerminalStatus


@dataclass(frozen=True)
class BehavioralConformance:
    shared_actions: frozenset[str]
    selection_matches: bool
    preservation_matches: bool
    compensation_matches: bool
    terminal_status_matches: bool
    unsupported_dimensions: tuple[str, ...]

    @property
    def passes_supported_subset(self) -> bool:
        return all(
            (
                self.selection_matches,
                self.preservation_matches,
                self.compensation_matches,
                self.terminal_status_matches,
            )
        )


def behavior_from_p1(plan, *, status: RecoveryStatus, final_state_correct: bool) -> RecoveryBehavior:
    return RecoveryBehavior(
        selected_actions=frozenset(plan.selected_invalidated_operations),
        preserved_actions=frozenset(plan.preserved_operations),
        compensation_actions=frozenset(action.operation_id for action in plan.compensation_actions if action.action_type.value == "COMPENSATE"),
        terminal_status=adapt_p1_terminal_status(status, final_state_correct=final_state_correct),
    )


def behavior_from_p4(plan: RecoveryPlan, outcome: RecoveryOutcome) -> RecoveryBehavior:
    return RecoveryBehavior(
        selected_actions=frozenset(plan.invalid_actions),
        preserved_actions=frozenset(plan.preserved_actions),
        compensation_actions=frozenset(step.action_id for step in plan.recovery_steps if step.step_type.value == "COMPENSATE"),
        terminal_status=outcome.status,
    )


def compare_supported_behavior(
    p1: RecoveryBehavior,
    p4: RecoveryBehavior,
    *,
    supported_action_ids: frozenset[str],
    unsupported_dimensions: tuple[str, ...] = (),
) -> BehavioralConformance:
    """Compare only operations represented by both engines.

    UNKNOWN propagation and durable adapter semantics are intentionally listed
    as unsupported rather than being silently treated as equivalent.
    """

    return BehavioralConformance(
        shared_actions=supported_action_ids,
        selection_matches=(p1.selected_actions & supported_action_ids) == (p4.selected_actions & supported_action_ids),
        preservation_matches=(p1.preserved_actions & supported_action_ids) == (p4.preserved_actions & supported_action_ids),
        compensation_matches=(p1.compensation_actions & supported_action_ids) == (p4.compensation_actions & supported_action_ids),
        terminal_status_matches=p1.terminal_status is p4.terminal_status,
        unsupported_dimensions=unsupported_dimensions,
    )
