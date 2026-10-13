# P4 Confirmatory Readiness Matrix

## Decision Basis

The proposed contribution is an evaluation framework and policy study, not a
new semantic selective-recovery algorithm. This matrix records readiness for
independent review and future design completion; it does not authorize a run.

| Requirement | Status | Supporting repository evidence | Exact action to resolve |
| --- | --- | --- | --- |
| Narrow contribution boundary | PASS | `P4_FINAL_PUBLICATION_POSITIONING.md`, `P4_NOVELTY_DECISION_REPORT.md`, manuscript contribution position | Maintain this wording in review materials. |
| Formal terminal/UNKNOWN specification | PARTIAL | `P4_C2_FORMAL_SAFETY_SPECIFICATION.md` defines S1-S5 and terminal truth table | Independent correctness reviewer must assess assumptions, invariants, and counterexamples. |
| Historical evidence preservation | PASS | Immutable P3 artifacts; P3-C9 report documents campaign separation | Preserve manifests/raw records and exclude them from confirmatory pooling. |
| Development implementation and tests | PARTIAL | Local provider, durable-receipt, evaluator-isolation, and behavioral tests | Demonstrate the same interfaces under curator-sealed templates. |
| Service-backed Temporal feasibility | PARTIAL | Real Java Workflow/Worker/Activity witness, common-metric evidence, and `P4_FAULT_SCHEDULING_FEASIBILITY_REPORT.md` | Implement the bounded shared fault-exposure protocol, then validate retry/deadline/restart evidence and sealed evaluation. |
| RETRO-inspired semantic baseline | PARTIAL | `effectguard.p4.retro_inspired`, paired development tests, and `P4_BASELINE_IMPLEMENTATION_REPORT.md` | Independently inspect the adaptation and run it in the shared sealed harness. |
| Independent benchmark provenance | BLOCKED | WfCommons importer/provenance materials; current overlays are synthetic | Curator selects licensed held-out templates and records provenance. |
| Independent annotations and hidden truth | BLOCKED | Existing annotations are EffectGuard-authored development overlays | Curator authors/approves effect contracts, invariants, and sealed outcome evaluator. |
| Leakage prevention | PARTIAL | Existing runtime/evaluator separation tests and P3 prompt/oracle checks | Apply the independent protocol, access boundaries, hashes, and audit logs to the new suite. |
| Capability-matched baseline contract | PARTIAL | Shared graph semantics, service witnesses, common metrics, root-compensation parity, and the minimum fault-exposure protocol | Root compensation now has an explicit contract; implement paired provider fault scripts and audited retry/deadline/restart traces before claiming capability matching. |
| Shared fault exposure | PARTIAL | `p4-shared-fault-script-v1`, provider audit ledger, and `P4_SHARED_FAULT_EXPOSURE_REPORT.md` | Integrate the script and audit references into both runtime arms; validate restarts and all required fault cases. |
| Positive and negative controls | PARTIAL | P4 S9 counterexamples and development controls | Curator includes required controls and at least one strong-baseline tie/win. |
| Statistical design | PARTIAL | `P4_STATISTICAL_PROTOCOL_REVIEW.md`, this checklist | Statistician approves template-level estimand, sensitivity, multiplicity, missing-data, and stopping rules. |
| Reproducible artifact pipeline | PARTIAL | P3 raw/manifests/reports and P4 development artifacts | Add one-command sealed-study analysis, environment pinning, checksums, and expected output verification. |
| SIGSOFT audit closure | PARTIAL | The historical SIGSOFT audit is excluded from this reviewer snapshot; the included external-review packages preserve the unresolved categories | Recreate or independently review the standards audit after citations and close independent-validation, calibration, fairness, and benchmark gaps. |
| Confirmatory protocol freeze | BLOCKED | Publication decision explicitly defers freeze | Resolve all external signoffs and blocked requirements; then produce a new versioned freeze decision. |

## Summary

**PASS** items show that the project has a candid contribution boundary and
preserved evidence. **PARTIAL** items show useful development infrastructure
but lack independent validation. **BLOCKED** items are indispensable and cannot
be resolved by additional self-authored runs.
