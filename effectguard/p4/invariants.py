"""Evaluator-side authoritative invariant checks for the local provider.

This module deliberately does not import the P4 recovery runtime or its
validity estimator. It consumes only provider-client observations after a run.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from ..models import ObservedStatus, ValidityResult
from .models import FinalValidationResult


class ProviderVerifier(Protocol):
    def verify(self, logical_operation_id: str):
        """Return authoritative provider state without exposing provider storage."""


@dataclass(frozen=True)
class AuthoritativeInvariantSuite:
    """Post-execution checks based on provider-owned durable state."""

    provider: ProviderVerifier

    def exactly_one_active(self, *logical_operation_ids: str) -> FinalValidationResult:
        active = []
        for logical_operation_id in logical_operation_ids:
            effect = self.provider.verify(logical_operation_id)
            if effect is not None and effect.observed_status is ObservedStatus.SUCCESS and not effect.compensated:
                active.append(logical_operation_id)
        if len(active) == 1:
            return FinalValidationResult(valid=True)
        return FinalValidationResult(valid=False, violated_invariants=(f"exactly_one_active:{','.join(logical_operation_ids)}",))

    def conflict_validity(self, *, primary_operation_id: str, fallback_operation_id: str) -> dict[str, str]:
        """Classify fallback validity from authoritative outcome after execution."""

        primary = self.provider.verify(primary_operation_id)
        if primary is None or primary.observed_status is ObservedStatus.UNKNOWN:
            result = ValidityResult.UNKNOWN
        elif primary.observed_status is ObservedStatus.SUCCESS and not primary.compensated:
            result = ValidityResult.INVALID
        else:
            result = ValidityResult.VALID
        return {fallback_operation_id: result.value}
