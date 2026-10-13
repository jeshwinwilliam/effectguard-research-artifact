"""Independent post-execution evaluation types.

This module deliberately does not import the P4 runtime or its estimator.
It evaluates serialized runtime decisions against evaluator-only benchmark
truth supplied by deterministic fixtures or a future isolated harness.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IndependentTruth:
    expected_validity: dict[str, str]
    invariants_hold: bool
    violated_invariants: tuple[str, ...] = ()


@dataclass(frozen=True)
class IndependentEvaluation:
    validity_mismatches: tuple[str, ...]
    recovered_with_invalid_invariants: bool
    violated_invariants: tuple[str, ...]

    @property
    def passes(self) -> bool:
        return not self.validity_mismatches and not self.recovered_with_invalid_invariants


class IndependentEvaluator:
    def evaluate(
        self,
        *,
        runtime_validity: dict[str, str],
        terminal_status: str,
        truth: IndependentTruth,
    ) -> IndependentEvaluation:
        mismatches = tuple(
            action_id
            for action_id, expected in sorted(truth.expected_validity.items())
            if runtime_validity.get(action_id) != expected
        )
        recovered_with_invalid_invariants = terminal_status == "RECOVERED" and not truth.invariants_hold
        return IndependentEvaluation(mismatches, recovered_with_invalid_invariants, truth.violated_invariants)
