# Fault Tolerance and Recovery Review

## Abstract

Assess ambiguous-effect handling, receipt durability, retry safety, and the
limits of the current provider-audited two-arm Temporal witness.

## Materials

- `P4_DURABLE_EFFECT_ADAPTER.md`
- `P4_SHARED_FAULT_EXPOSURE_REPORT.md`
- `P4_SHARED_FAULT_EXPOSURE_FAIRNESS_MATRIX.md`
- `P4_SHARED_FAULT_EXPOSURE_REPRODUCIBILITY.md`
- `paper/release_candidate/REPRODUCIBILITY_GUIDE.md`
- `paper/release_candidate/EXPECTED_RESULTS.md`
- `paper/reviewer_distribution/EXCLUDED_EVIDENCE_NOTICE.md`

## Questions

1. Does the provider audit distinguish before-commit from after-commit loss?
2. Is retry behavior safe under stable logical IDs and idempotency keys?
3. Which compensation or receipt assumptions remain untested?
4. What restart/interruption evidence is indispensable before comparison?
5. Does the witness support its stated narrow claim and no more?

## Reproduction and Deliverable

Follow `P4_SHARED_FAULT_EXPOSURE_REPRODUCIBILITY.md`. Return a memo identifying
unjustified inference, missing fault cases, and any unsafe retry/compensation
condition. The historical raw reconciliation trace is excluded; reviewers should
base feedback on fresh local audit evidence or explicitly identify unavailable
historical evidence as a limitation.

## Feedback Template

`Reviewer role:`
`Reproduced: YES / NO`
`Audit-evidence concern:`
`Failure-mode gap:`
`Required control:`
`Blocking status: BLOCKING / NONBLOCKING`
