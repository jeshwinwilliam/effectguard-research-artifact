# Correctness and Novelty Review

## Abstract

Assess whether the formal safety argument is coherent and whether the proposed
UNKNOWN-aware receipt policy is distinguishable from RETRO-style repair and a
capability-matched Temporal application.

## Materials

- `P4_C2_FORMAL_SAFETY_SPECIFICATION.md`
- `paper/P4_DEVELOPMENT_EVIDENCE_FREEZE.md`
- `paper/P4_SUPPORTED_CLAIMS_MATRIX.md`
- `paper/P4_RETRO_DEEP_COMPARISON.md`
- `paper/P4_TEMPORAL_EQUIVALENCE_CHALLENGE.md`

## Questions

1. Are S1-S5 conditional safety properties stated with sufficient assumptions?
2. Are UNKNOWN transitions and terminal precedence sound under lost replies?
3. What smallest counterexample invalidates the proposed policy boundary?
4. Is any novelty claim defensible beyond RETRO and programmable Temporal?
5. Which claims should be removed before external benchmarking?

## Reproduction and Deliverable

Read the listed specifications and inspect `tests/test_p4_unknown_safe_recovery.py`.
Return a short memo with assumptions accepted, counterexamples, novelty risks,
and required corrections. Do not endorse the paper.

## Feedback Template

`Reviewer role:`
`Conflicts:`
`Safety concern or counterexample:`
`Novelty assessment:`
`Required change:`
`Blocking status: BLOCKING / NONBLOCKING`
