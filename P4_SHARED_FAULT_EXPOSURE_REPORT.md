# P4 Shared Fault Exposure Report

## Implemented Provider Boundary

The local P4 provider now accepts `p4-shared-fault-script-v1` and persists an
append-only `provider_audit` ledger. The implemented script supports a
deterministic retryable submit failure before commit and a lost acknowledgement
after a committed effect. The ledger records script loading, submit request,
pre-commit failure, commit, withheld acknowledgement, receipt resolution,
verification, duplicate submit, and compensation request/outcome.

`experiments/p4/shared_fault_script_v1.json` is a development-only example.
The standalone provider accepts it through `--fault-script`; HTTP clients can
read the authoritative ledger at `/audit`. A `503` represents the scripted
retryable transport failure. This is provider evidence, not an inference from
runtime histories.

## Validation

Focused provider and common-execution tests passed: `9 passed in 0.14s`.
The provider regression verifies the pre-commit failure occurs before the
commit audit event, the following submission commits, the acknowledgement is
withheld, and later resolution/verification are auditable.

The full Python suite passed: `197 passed in 33.99s`. Java unit tests passed;
the five service-backed test classes remain opt-in and were skipped without
their required local-service properties. No explicit shared-fault service test
was run because neither runtime arm yet receives the same script end to end.

## Two-Arm Scripted Witness

The common harness now passes a provider-owned retryable transport failure to
both real arms. EffectGuard retries only `ProviderTransientError` up to the
public schedule budget; Temporal retains its native Activity retry. Fresh
isolated providers loaded from the same script ran
`travel_positive_gap_success` through the real EffectGuard runtime and a real
Temporal Workflow/Worker/Activity implementation.

Both provider audits contained `submit_failed_before_commit`, `effect_committed`,
`acknowledgement_withheld`, and `receipt_resolved`. Both arms reached
`RECOVERED`, with one retry, two provider submissions, two provider
verifications, and one actual descendant effect. Temporal separately recorded
two scheduler/replay events. The evidence is
`results/p4/two-arm-fault-exposure-v1/scripted_retry_lost_ack_reconciliation.json`.

## Remaining Integration Gaps

This sprint did not complete fair paired execution for the full matrix:

- The script identity and audit reference are not yet embedded in the Temporal
  witness file, although the authoritative provider audits were retrieved by
  endpoint for the paired witness.
- Provider interruption, worker interruption/restart, retry exhaustion, and
  observation-deadline scripts are not implemented.
- The existing Temporal restart test uses an in-memory activity provider, not
  this shared provider-audit boundary.

Therefore no new paired case is classified FAIR_AND_VERIFIED. Existing P4
development artifacts remain unchanged, and no confirmatory workflow was run.

SHARED FAULT EXPOSURE PARTIAL — NARROW CLAIMS OR FIX CRITICAL DEFECT
