# P4 Primary Research Question

## Primary Question

Can an independently curated and reproducible evaluation framework based on
provider receipts, declared external-effect capabilities, hidden final-state
invariants, and capability-matched baselines reliably expose safety,
selectivity, and availability tradeoffs among recovery policies for ambiguous
external-tool outcomes?

The object of comparison includes EffectGuard's explicit
`VALID`/`INVALID`/`UNKNOWN` policy, but the question does not presume that this
policy is algorithmically new or superior.

## Supporting Questions

1. Under the same stable logical IDs, verification, idempotency, compensation,
   dependency/conflict contract, and deadline, does the explicit UNKNOWN policy
   differ from durable replay and a RETRO-like semantic policy in unsafe final
   states, recovery work, or blocked/unresolved outcomes?
2. Do observed tradeoffs persist across independently authored workflow
   templates and domains, including positive controls where the policy can help
   and negative controls where a strong baseline matches or outperforms it?

## Exact Problem

External tool calls can commit despite a timeout or delayed observation. Durable
replay and idempotency can preserve workflow progress and prevent duplicates;
semantic recovery can preserve downstream work when its inputs remain
equivalent. What remains to be measured is whether a reusable, auditable
evaluation contract can faithfully expose the policy decisions required when
runtime evidence is insufficient to decide whether an irreversible external
effect occurred.

## Assumptions

- The tool contract honestly declares stable IDs, verification, idempotency,
  reversibility, and compensation capabilities.
- Runtime policy cannot read evaluator-only truth.
- Curators independently author or approve templates, annotations, final
  invariants, fault schedules, and held-out outcomes.
- Baselines receive identical public evidence and provider capabilities.
- The primary statistical unit is an independent workflow template.

## Falsification Criteria

The full-paper premise fails if any of the following holds:

1. Independent reviewers judge the framework's receipt/capability abstraction
   to be redundant with existing benchmark or recovery frameworks.
2. EffectGuard's policy has no meaningful difference from capability-matched
   Temporal replay and RETRO-like semantic recovery after blocked/unresolved
   outcomes are counted.
3. Apparent benefits vanish on independently authored templates or are caused
   by EffectGuard-specific annotations, evaluator leakage, or unequal provider
   features.
4. Any `RECOVERED` outcome violates a sealed final invariant.
5. The framework cannot preserve mixed and negative results, including the
   equivalent of P3 S9, in a reproducible artifact.

## Strongest Fair Baselines

1. Durable Temporal workflow with the same stable IDs, provider verification,
   idempotency, compensation, and final evaluator.
2. Semantic selective-recovery policy modeled on RETRO's equivalence/predicate
   approach with explicit pause or escalation for unresolved external effects.
3. Idempotency-aware retry/replay, included only as a weaker diagnostic
   baseline rather than evidence against the stronger two baselines.
