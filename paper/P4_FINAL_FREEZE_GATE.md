# P4 Final Confirmatory Freeze Gate

## Current Decision

**Do not freeze or authorize confirmatory evaluation.** The repository is ready
to request independent review of the proposed design, but indispensable
external conditions remain unresolved.

## Required Signoffs

| Reviewer | Decision requested | Minimum evidence to inspect | Required outcome before freeze |
| --- | --- | --- | --- |
| Distributed-systems correctness reviewer | Are terminal-state rules, provider assumptions, UNKNOWN transitions, and evaluator isolation sound under the stated model? | P4 safety specification, counterexamples, receipt/provider contracts, runtime/evaluator boundary. | Written assessment identifying accepted assumptions and unresolved counterexamples. |
| Benchmark curator | Are workflow provenance, licenses, synthetic annotations, hidden truth, controls, and leakage barriers independent and suitable? | Benchmark protocol, source topologies, annotation schema, curator access plan. | Sealed, versioned benchmark package with provenance and explicit synthetic-overlay labels. |
| Statistical reviewer | Is the template-level paired design capable of supporting the stated inference without selective attrition? | Primary question, metric definitions, sensitivity plan, missing-data and stopping rules. | Approved or revised analysis plan before any outcome access. |
| Temporal/RETRO baseline reviewer | Are the strong baseline designs faithful and capability-matched? | Baseline fidelity requirements, Temporal implementation, planned RETRO-inspired adaptation, shared provider contract. | Written confirmation or required corrections before implementation freeze. |

## Reviewer Checklists

### Correctness and Invariant Soundness

- [ ] `RECOVERED` requires independent final-invariant success.
- [ ] `UNKNOWN` cannot justify irreversible conflicting progress.
- [ ] Provider verification, idempotency, compensation, and receipt assumptions
  are explicit and appropriately conditional.
- [ ] `BLOCKED`, `UNRESOLVED`, `RECOVERY_UNSUPPORTED`, `FAILED`, and `UNSAFE`
  are distinguishable and truthfully reported.
- [ ] Runtime code cannot inspect evaluator-only truth.
- [ ] Known counterexamples, especially delayed success and failed
  compensation, remain testable negative cases.

### Benchmark Independence and Annotation Validity

- [ ] Topology provenance, version, and license permit use and redistribution.
- [ ] Effect annotations distinguish supported facts from synthetic overlays.
- [ ] Curator, developers, and evaluators have appropriate information
  separation and conflict disclosure.
- [ ] Final invariants and fault truth are withheld from runtime policy.
- [ ] Included controls can falsify a policy advantage.
- [ ] Exclusion criteria are set before arm outcomes are visible.

### Statistical Design

- [ ] Independent template is the primary unit.
- [ ] Paired groups share initial state, public evidence, and fault schedule.
- [ ] Safety and availability are analyzed jointly rather than completion only.
- [ ] Confidence intervals, multiplicity, sensitivity, missing-data, and
  incomplete-pair rules are approved prospectively.
- [ ] Safety failure, provider failure, and baseline win cannot be hidden or
  replaced through selective retry.

### Temporal and RETRO Baseline Fidelity

- [ ] Temporal uses a real service and the shared provider contract.
- [ ] Temporal application policy is distinguished from Temporal-native replay.
- [ ] RETRO-inspired work is labeled as an adaptation, not the RETRO system.
- [ ] All strong arms receive the same IDs, verification, idempotency,
  compensation, dependencies, deadlines, and evaluator.
- [ ] A shared scheduler makes paired public observations identical.
- [ ] Any arm that cannot meet these conditions remains in the report as a
  feasibility limitation, not an omitted comparison.

## Freeze Preconditions

All conditions below must be true before a separate, versioned protocol-freeze
decision can be considered:

1. Independent reviewers have provided actual, recorded feedback; no approval
   may be inferred from this checklist.
2. A curator has delivered a licensed, held-out benchmark with sealed truth.
3. The capability-matched Temporal and RETRO-inspired arms are implemented and
   pass pre-outcome fidelity checks under the shared harness.
4. The statistical reviewer has approved the design and sensitivity rationale.
5. Public contracts, prompts where applicable, seeds, retry/timeout behavior,
   exclusion rules, and analysis scripts are versioned and hashed.
6. The study package can preserve raw data, incomplete groups, provider
   failures, baseline wins, and safety failures without manual rewriting.

## Current Blockers

- No independent correctness, curation, statistics, or baseline-fidelity
  feedback has been received.
- No curator-sealed workflow/effect/invariant package exists.
- The RETRO-inspired baseline is not implemented.
- Temporal is feasible but not paired and capability-matched in a common
  confirmatory harness.
- No prospective template-level sensitivity/power rationale is approved.

## Conclusion

The project is ready for external review of the design documents, not ready
for a confirmatory freeze. Any change to these requirements after sealed
outcomes are available must be treated as a new study version.
