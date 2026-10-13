# P4 Final Research Question Candidate

## Primary Research Question

For independently authored workflow templates that invoke external tools with
stable logical operation IDs, declared capability contracts, and potentially
ambiguous commit outcomes, does an explicit `VALID`/`INVALID`/`UNKNOWN`
recovery policy with conflict-cone blocking reduce unsafe terminal outcomes or
unnecessary recovery work relative to capability-matched durable replay and
semantic selective-recovery policies, without increasing unresolved or blocked
outcomes beyond a pre-specified practical bound?

This is a falsifiable policy-comparison question. It does not assume that the
policy is a new recovery algorithm or that its answer favors EffectGuard.

## System and Failure Model

- A workflow invokes provider tools that may return success, failure, timeout,
  delayed visibility, duplicate delivery, or an externally committed outcome
  that is not immediately observable to the caller.
- Each operation has a stable logical ID and a declared contract for
  idempotency, verification, reversibility, and compensation.
- The runtime sees only receipts, public workflow state, declared contracts,
  and allowed provider verification responses. It does not receive hidden
  evaluator truth.
- The evaluator observes authoritative final provider state only after the run
  and checks versioned final invariants.
- Fault schedules, tool contracts, prompts where applicable, and evaluation
  seeds are sealed before execution.

## Safety Properties

1. A `RECOVERED` result must satisfy every independent final-state invariant.
2. An irreversible operation that conflicts with an unresolved effect must not
   be executed unless runtime-visible evidence certifies the prerequisite.
3. The runtime must not claim a verified external effect without a receipt or
   authoritative verification response permitted by the provider contract.
4. In the absence of sufficient evidence, the allowed outcomes are `BLOCKED`,
   `UNRESOLVED`, `RECOVERY_UNSUPPORTED`, or `FAILED`, not optimistic recovery.

## Required Assumptions

- Logical IDs are stable across retry, replay, and crash recovery.
- Provider capability declarations are accurate for the evaluated tools.
- Authoritative verification and compensation, when declared, are trustworthy.
- The dependency/conflict contract is independently reviewed and is not
  derived from hidden evaluator outcomes.
- Final invariants represent the claimed safety condition for each template.

## Capability-Matched Baselines

Every baseline receives the same workflow template, tool interface, logical
operation IDs, provider verification, idempotency support, compensation
capabilities, declared dependency/conflict structure, retry budget, deadline,
and final-invariant evaluator. At minimum, compare:

1. Durable replay with idempotency and verification.
2. A semantic selective-recovery policy resembling RETRO's use of
   equivalence/predicates and explicit pause/escalation for unresolved effects.
3. The same durable application with EffectGuard's explicit `UNKNOWN` and
   conflict-cone policy.

## Experimental Unit and Outcomes

The primary unit is an independently authored workflow template, not a seed or
an individual tool call. Paired strategy executions share a template, provider
contract, and fault schedule. Report at least:

- Unsafe recovered-terminal rate, with independent invariant failures.
- Recovery precision and recall for actions selected for repair where a sealed
  oracle defines the affected set.
- Recovery work: actions re-executed, compensations, and provider calls.
- Availability cost: `BLOCKED`, `UNRESOLVED`, and `RECOVERY_UNSUPPORTED` rates
  plus time to safe terminal state.
- Operational overhead: receipt storage, verification calls, and latency.
- Failure taxonomy, missing data, and incomplete pairing.

## Falsification Conditions

The policy claim fails if any of the following occurs in a frozen,
independently curated study:

1. EffectGuard returns `RECOVERED` for a run whose final invariant fails.
2. A capability-matched durable replay or RETRO-like semantic baseline attains
   the same safety with equal or lower recovery work and no worse availability
   across the primary template-level analysis.
3. EffectGuard's apparent work reduction is explained by more `BLOCKED`,
   `UNRESOLVED`, or excluded/incomplete outcomes.
4. The result disappears when semantic-gap labels, annotations, or final
   invariants are independently authored and sealed.
5. A strong baseline outperforms EffectGuard on a pre-specified scenario
   family, including the E2 semantic-preservation or E6 unsupported-recovery
   controls in `P4_MINIMAL_DISTINGUISHING_COUNTEREXAMPLES.md`.

## Interpretation Rules

A tie with the capability-matched semantic baseline supports neither a new
algorithm nor a performance claim. It may still support reusable software or
evaluation-framework value if independent reviewers find that contribution
useful. A loss is a valid result and must be reported without post-hoc changes
to the policy or task suite.
