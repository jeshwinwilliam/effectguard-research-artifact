# P4 Baseline Fidelity Requirements

## Principle

The confirmatory comparison is between recovery *policies under identical
capabilities*, not between an enriched EffectGuard runtime and weakened
alternatives. Every arm receives the same public workflow definition, stable
logical IDs, provider implementation, verification access, idempotency,
compensation contract, dependency/conflict declarations, fault schedule,
deadline, retry budget, and post-execution evaluator.

## Required Arms and Current Status

| Arm | Required confirmatory behavior | Current repository status | Readiness |
| --- | --- | --- | --- |
| EffectGuard | Receipt-based `VALID`/`INVALID`/`UNKNOWN` classification; conflict-cone barrier; typed terminal outcomes; no evaluator truth at runtime. | Implemented and deterministically tested with local provider/receipt stores. | PARTIAL: needs curator-sealed inputs and shared harness. |
| Temporal plus application-level UNKNOWN handling | Real Temporal service workflow using the same provider contract, stable IDs, verification, idempotency, compensation, and the same explicit policy. This is an application configuration, not claimed native Temporal behavior. | Service-backed Java Workflow/Worker/Activity tests now execute delayed success/failure, persistent UNKNOWN, unsupported compensation, and retry-idempotency against the P4 provider; a separate deterministic paired harness validates the matching application policy contract. | PARTIAL: not yet paired under one real-service scheduler, action graph, deadline, or evaluator. |
| RETRO-inspired semantic recovery | A newly implemented baseline that uses documented semantic-equivalence predicates and selective re-execution, with explicit pause/escalation when external effects cannot be resolved. It must be labeled inspired by RETRO, not RETRO. | `effectguard.p4.retro_inspired` implements a development-only adaptation and paired tests. | PARTIAL: requires independent fidelity review and the shared sealed harness. |
| Idempotency-aware replay | Retry/replay using the same stable IDs, provider deduplication, verification, and declared compensation. It must not receive fewer provider capabilities than EffectGuard. | Development baseline exists in P4 scenarios. | PARTIAL: needs shared confirmatory harness. |
| Dependency-only recovery | Select graph descendants based on declared dependencies without semantic equivalence/predicate refinement. | Implemented in P1/P2/P3 deterministic paths. | PARTIAL: needs independent annotations and shared harness. |
| Checkpoint/restart | Restore/replay from the same available checkpoint and use the shared provider contract. | Implemented as deterministic development baselines. | PARTIAL: needs capability-matched confirmation. |
| Blocking | Withhold progress on unresolved evidence and report the same terminal taxonomy; it may verify but must not use hidden truth. | Implemented in deterministic paths. | PARTIAL: needs shared confirmatory harness. |

## Shared Capability Contract

For each operation and each arm, the manifest must record:

- workflow and operation IDs;
- provider request/idempotency keys;
- observed receipt and verification response;
- reversibility, compensation, and verification capability;
- dependency and conflict edges available to the arm;
- retry policy, deadline, and operation ordering;
- runtime terminal result and independent evaluator verdict.

Any baseline unable to use a capability available to EffectGuard must be split
into an explicitly weaker diagnostic arm, not used as evidence of superiority.

## Temporal Fidelity Rules

1. Use a real Temporal service for the confirmatory baseline, not a Python
   replay model or an SDK test service presented as Temporal.
2. Pin service, SDK, Java, persistence, and worker versions in the manifest.
3. Model external calls as Activities that use the same stable IDs and provider
   API as EffectGuard.
4. Separate Temporal's durable replay/retry from any application-defined
   semantic predicate or UNKNOWN policy in reporting.
5. Pair runs under one fault scheduler and equivalent timeout/deadline budget.
6. Retain Temporal wins, ties, unavailable outcomes, and provider failures.

### Current Service-Backed Scope

`ServiceBackedProviderOutcomeMatrixTest` is opt-in and runs a real local
Temporal development server, Java Worker, Workflow, and HTTP Activity against
the P4 local provider. It establishes that the Temporal arm can consume the
shared provider's receipt/verification and compensation contract under several
development outcome states. It does not establish equal scheduling or semantic
descendant handling with EffectGuard: the current Java workflow has no common
cross-runtime action graph runner and does not execute EffectGuard's runtime in
the same service-backed test. These differences are disqualifying for a
comparative claim until the common harness exists.

### Common Harness Update

`effectguard.p4.common_execution` now supplies a deterministic public workflow
specification to the real EffectGuard runtime and the real Temporal service
adapter. The Temporal witness verifies matching workflow IDs, operation IDs,
and graph hash at the integration boundary. This closes the prior
no-common-input gap, but not the semantic-execution gap: the Java Workflow
does not yet execute graph descendants or consume the independent evaluator.
The common harness therefore remains development-only and PARTIAL for
capability-matched baseline fidelity.

## RETRO-Inspired Fidelity Rules

1. Cite RETRO as the design source; do not call the implementation RETRO.
2. Implement an action history/dependency representation and a versioned
   equivalence predicate over the same public inputs provided to EffectGuard.
3. Re-execute only when the predicate says inputs materially changed; preserve
   equivalent actions.
4. For unresolved external effects, use a pre-specified pause/escalation rule
   with typed terminal outcomes. Do not retrofit EffectGuard's result labels
   after seeing outcomes.
5. Have a reviewer inspect the predicate and graph contract before execution.

## Fairness Checks Before Any Run

- Same initial-state hash per paired group.
- Same provider-state trajectory and public observations.
- Same effect capabilities and logical-ID namespace semantics.
- Same number of permitted verification and compensation calls, or an explicit,
  pre-specified reason for a difference.
- Same evaluator, invariant suite, and terminal-status interpretation.
- No arm-specific prompt, oracle data, task definition, or fault ordering.

## Disqualifying Conditions

Do not make a comparative claim if the Temporal or RETRO-inspired arm is
missing, receives reduced capabilities, has a different deadline/fault
schedule, accesses a different provider state, or cannot be evaluated with the
same final invariants. Report feasibility failures rather than silently
dropping the arm.
