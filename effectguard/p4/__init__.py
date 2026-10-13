"""P4 UNKNOWN-safe recovery primitives.

The P4 runtime intentionally keeps its recovery estimator separate from the
independent evaluator used by deterministic correctness tests.
"""

from .conformance import adapt_p1_terminal_status
from .durable import DurableReceiptStore
from .invariants import AuthoritativeInvariantSuite
from .local_provider import LocalEffectProvider, LocalProviderClient
from .models import (
    ActionDescriptor,
    EffectLedger,
    EffectReceipt,
    FinalValidationResult,
    ProviderCapabilities,
    RecoveryOutcome,
    RecoveryPlan,
    RecoveryRequest,
    RecoveryTerminalStatus,
)
from .runtime import EvidenceValidityEstimator, UnknownSafeRecovery

__all__ = [
    "ActionDescriptor",
    "AuthoritativeInvariantSuite",
    "DurableReceiptStore",
    "EffectLedger",
    "EffectReceipt",
    "EvidenceValidityEstimator",
    "FinalValidationResult",
    "LocalEffectProvider",
    "LocalProviderClient",
    "ProviderCapabilities",
    "RecoveryOutcome",
    "RecoveryPlan",
    "RecoveryRequest",
    "RecoveryTerminalStatus",
    "UnknownSafeRecovery",
    "adapt_p1_terminal_status",
]
