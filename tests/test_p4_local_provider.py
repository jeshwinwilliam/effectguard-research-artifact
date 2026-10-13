from __future__ import annotations

from pathlib import Path

import pytest

from effectguard.models import EffectClass, ObservedStatus, ValidityResult
from effectguard.p4.evaluator import IndependentEvaluator, IndependentTruth
from effectguard.p4.invariants import AuthoritativeInvariantSuite
from effectguard.p4.local_provider import FaultScript, LocalEffectProvider, ProviderError, ProviderTransientError


def _submit(provider: LocalEffectProvider, logical_operation_id: str, *, acknowledge: bool = True, compensation: bool = True):
    return provider.submit(
        logical_operation_id=logical_operation_id,
        idempotency_key=f"{logical_operation_id}-key",
        effect_class=EffectClass.IRREVERSIBLE,
        supports_compensation=compensation,
        acknowledge=acknowledge,
    )


def test_local_provider_models_timeout_delayed_resolution_and_idempotent_duplicate(tmp_path: Path) -> None:
    database = tmp_path / "provider.sqlite"
    provider = LocalEffectProvider(database)
    try:
        timed_out = _submit(provider, "job-a", acknowledge=False)
        assert timed_out.acknowledged is False
        assert timed_out.timed_out is True
        assert timed_out.effect.observed_status is ObservedStatus.UNKNOWN

        duplicate = _submit(provider, "job-a")
        assert duplicate.duplicate is True
        assert duplicate.effect.provider_reference == timed_out.effect.provider_reference

        resolved = provider.resolve("job-a", ObservedStatus.SUCCESS)
        assert resolved.observed_status is ObservedStatus.SUCCESS
        assert provider.verify("job-a") == resolved
        assert provider.compensate("job-a").compensated is True
    finally:
        provider.close()

    restarted_provider = LocalEffectProvider(database)
    try:
        restored = restarted_provider.verify_required("job-a")
        assert restored.observed_status is ObservedStatus.SUCCESS
        assert restored.compensated is True
    finally:
        restarted_provider.close()


def test_local_provider_rejects_unsupported_compensation_and_conflicting_outcomes(tmp_path: Path) -> None:
    provider = LocalEffectProvider(tmp_path / "provider.sqlite")
    try:
        _submit(provider, "job-a", compensation=False)
        provider.resolve("job-a", ObservedStatus.SUCCESS)
        with pytest.raises(ProviderError, match="compensation unsupported"):
            provider.compensate("job-a")
        with pytest.raises(ProviderError, match="conflicting decisive"):
            provider.resolve("job-a", ObservedStatus.FAILURE)
    finally:
        provider.close()


def test_provider_fault_script_and_audit_preserve_pre_and_post_commit_boundaries(tmp_path: Path) -> None:
    provider = LocalEffectProvider(
        tmp_path / "provider.sqlite",
        fault_script=FaultScript("retry-and-lost-ack", submit_failures_before_commit=1, lose_acknowledgement_after_commit=True),
    )
    try:
        with pytest.raises(ProviderTransientError, match="before commitment"):
            _submit(provider, "job-a")
        acknowledgement = _submit(provider, "job-a")
        assert acknowledgement.timed_out is True
        assert acknowledgement.effect.observed_status is ObservedStatus.UNKNOWN
        provider.resolve("job-a", ObservedStatus.SUCCESS)
        provider.verify_required("job-a")
        events = [event.event for event in provider.audit_events()]
        assert events.index("submit_failed_before_commit") < events.index("effect_committed")
        assert "acknowledgement_withheld" in events
        assert "receipt_resolved" in events
        assert "verification_requested" in events
    finally:
        provider.close()


def test_authoritative_invariant_suite_detects_a_corrupted_runtime_validity_decision(tmp_path: Path) -> None:
    provider = LocalEffectProvider(tmp_path / "provider.sqlite")
    try:
        _submit(provider, "primary")
        _submit(provider, "fallback")
        provider.resolve("primary", ObservedStatus.SUCCESS)
        provider.resolve("fallback", ObservedStatus.SUCCESS)

        invariants = AuthoritativeInvariantSuite(provider)
        final_state = invariants.exactly_one_active("primary", "fallback")
        expected_validity = invariants.conflict_validity(
            primary_operation_id="primary",
            fallback_operation_id="fallback",
        )
        evaluation = IndependentEvaluator().evaluate(
            runtime_validity={"fallback": ValidityResult.VALID.value},
            terminal_status="RECOVERED",
            truth=IndependentTruth(
                expected_validity=expected_validity,
                invariants_hold=final_state.valid,
                violated_invariants=final_state.violated_invariants,
            ),
        )

        assert expected_validity == {"fallback": ValidityResult.INVALID.value}
        assert evaluation.validity_mismatches == ("fallback",)
        assert evaluation.recovered_with_invalid_invariants is True
        assert evaluation.passes is False
    finally:
        provider.close()


def test_runtime_source_cannot_reach_provider_or_evaluator_invariant_logic() -> None:
    runtime_source = Path("effectguard/p4/runtime.py").read_text(encoding="utf-8")
    invariant_source = Path("effectguard/p4/invariants.py").read_text(encoding="utf-8")

    assert "local_provider" not in runtime_source
    assert "from .invariants" not in runtime_source
    assert "from .runtime" not in invariant_source
