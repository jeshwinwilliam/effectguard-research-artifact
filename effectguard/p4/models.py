from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from ..models import EffectClass, ObservedStatus, ValidityResult


class RecoveryTerminalStatus(str, Enum):
    RECOVERED = "RECOVERED"
    BLOCKED = "BLOCKED"
    UNRESOLVED = "UNRESOLVED"
    RECOVERY_UNSUPPORTED = "RECOVERY_UNSUPPORTED"
    FAILED = "FAILED"
    UNSAFE = "UNSAFE"


class RecoveryStepType(str, Enum):
    RECOMPUTE = "RECOMPUTE"
    COMPENSATE = "COMPENSATE"
    REEXECUTE = "REEXECUTE"


@dataclass(frozen=True)
class ProviderCapabilities:
    supports_idempotency: bool = False
    supports_deduplication_lookup: bool = False
    supports_verification: bool = False
    supports_compensation: bool = False


@dataclass(frozen=True)
class EffectReceipt:
    logical_operation_id: str
    effect_class: EffectClass
    observed_status: ObservedStatus
    provider_reference: str | None
    idempotency_key: str | None
    capabilities: ProviderCapabilities

    def __post_init__(self) -> None:
        if not self.logical_operation_id:
            raise ValueError("effect receipts require a logical operation identifier")


@dataclass(frozen=True)
class ActionDescriptor:
    action_id: str
    logical_operation_id: str
    effect_class: EffectClass
    requires_effects: tuple[str, ...] = ()
    conflicts_with_effects: tuple[str, ...] = ()
    capabilities: ProviderCapabilities = field(default_factory=ProviderCapabilities)

    def __post_init__(self) -> None:
        if not self.logical_operation_id:
            raise ValueError("actions require a logical operation identifier")


@dataclass(frozen=True)
class RecoveryRequest:
    workflow_id: str
    actions: tuple[ActionDescriptor, ...]
    receipts: tuple[EffectReceipt, ...]
    required_invariants: tuple[str, ...]
    evidence_deadline_expired: bool = False

    def receipt_index(self) -> dict[str, EffectReceipt]:
        return {receipt.logical_operation_id: receipt for receipt in self.receipts}


@dataclass(frozen=True)
class ValidityCertificate:
    action_id: str
    result: ValidityResult
    evidence_ids: tuple[str, ...]
    reason: str


@dataclass(frozen=True)
class RecoveryStep:
    action_id: str
    step_type: RecoveryStepType
    reason: str


@dataclass(frozen=True)
class RecoveryAuditRecord:
    event: str
    action_id: str | None
    evidence_ids: tuple[str, ...]
    detail: str


@dataclass(frozen=True)
class RecoveryPlan:
    workflow_id: str
    certificates: tuple[ValidityCertificate, ...]
    preserved_actions: tuple[str, ...]
    deferred_actions: tuple[str, ...]
    invalid_actions: tuple[str, ...]
    recovery_steps: tuple[RecoveryStep, ...]
    terminal_status: RecoveryTerminalStatus | None
    audit_records: tuple[RecoveryAuditRecord, ...]


@dataclass(frozen=True)
class FinalValidationResult:
    valid: bool
    violated_invariants: tuple[str, ...] = ()


@dataclass(frozen=True)
class RecoveryOutcome:
    status: RecoveryTerminalStatus
    plan: RecoveryPlan
    final_validation: FinalValidationResult | None
    audit_records: tuple[RecoveryAuditRecord, ...]


@dataclass(frozen=True)
class LedgerDecision:
    accepted: bool
    terminal_status: RecoveryTerminalStatus | None
    reason: str


@dataclass
class EffectLedger:
    """In-memory logical-ID guard used by deterministic P4 tests.

    A durable provider-backed implementation is intentionally out of scope for
    Sprint 1; callers must declare whether deduplication can be trusted.
    """

    _submitted: dict[str, EffectReceipt] = field(default_factory=dict)

    def register_submission(self, receipt: EffectReceipt) -> LedgerDecision:
        existing = self._submitted.get(receipt.logical_operation_id)
        if existing is None:
            self._submitted[receipt.logical_operation_id] = receipt
            return LedgerDecision(True, None, "new logical operation accepted")
        if receipt.capabilities.supports_deduplication_lookup:
            return LedgerDecision(
                False,
                RecoveryTerminalStatus.BLOCKED,
                "duplicate logical operation rejected by provider deduplication",
            )
        return LedgerDecision(
            False,
            RecoveryTerminalStatus.RECOVERY_UNSUPPORTED,
            "duplicate logical operation cannot be safely checked without provider deduplication",
        )

    def update_observation(self, receipt: EffectReceipt) -> None:
        """A later provider observation replaces only the matching logical receipt."""

        if receipt.logical_operation_id in self._submitted:
            self._submitted[receipt.logical_operation_id] = receipt
