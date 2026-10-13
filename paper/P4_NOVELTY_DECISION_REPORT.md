# P4 Novelty Decision Report

## Decision

**Selected novelty boundary: C, a reusable implementation and evaluation
framework, with B, a formally specified safety policy, as a conditional
secondary contribution.**

The available evidence does not support A, a new recovery algorithm. RETRO
already supplies semantic predicates, dependency tracking, selective
re-execution, and compensating treatment of external effects. The available
evidence also does not yet support D, an empirical characterization of policy
tradeoffs, because the current P3/P4 data are exploratory and rely on
EffectGuard-authored development workloads.

## Adversarial Findings

| Challenge | Finding | Consequence |
| --- | --- | --- |
| RETRO | RETRO repairs from an action history graph, skips semantically equivalent actions, selectively re-executes affected work, and handles external dependencies through compensation, resend, or administrator resolution. | Remove all broad semantic-selective-recovery novelty claims. |
| Ambiguous external effects | RETRO does not present an explicit provider receipt model or three-valued automatic outcome policy. It pauses/escalates when it cannot safely repair external dependencies. | `UNKNOWN` is a potential policy/interface distinction, not an established algorithmic difference. |
| Temporal | A Temporal application can durably persist history and implement stable IDs, receipts, verification, predicates, barriers, compensation, and typed unresolved states in application code. | Do not compare against weakened Temporal replay. Evaluate policy configurations with matched capabilities. |
| Counterexamples | Ordinary retry loses on ambiguous, irreversible conflicts, but a semantic baseline or capability-complete Temporal workflow can encode the same conservative rule. | Any advantage must be empirical, with blocking and unresolved outcomes counted as costs. |
| Current evidence | P3 is diagnostic and P4 is deterministic development-only evidence with EffectGuard-authored annotations. | No confirmatory novelty, safety-rate, generalization, or superiority claim is justified. |

## Defensible Contribution Statement

EffectGuard is a research framework for specifying and evaluating conservative
recovery policies for agent workflows that face ambiguous external-tool
outcomes. It makes provider-facing receipt evidence, capability declarations,
three-valued runtime decisions, conflict-cone barriers, and post-execution
evaluator isolation explicit and testable.

The framework's policy may be useful if, on independently curated workflows,
it demonstrates a favorable and reproducible safety, recovery-work, and
availability tradeoff against capability-matched durable and semantic-recovery
baselines. This is a hypothesis rather than a result.

## Claims Excluded Before Review

- A first or generally new semantic selective-recovery algorithm.
- Inherent superiority over Temporal, RETRO, Sagas, or idempotency-aware retry.
- General safety for real agent systems or arbitrary providers.
- Independent validation, external review, or confirmed novelty.

## Preconditions for External Review

1. Ask a distributed-systems reviewer whether the proposed receipt and
   `UNKNOWN` policy boundary is technically meaningful beyond RETRO-style
   pause/escalation.
2. Ask a benchmark curator to independently author or approve workflow
   annotations, fault schedules, final invariants, and hidden truth.
3. Add a capability-matched Temporal policy baseline and a RETRO-like semantic
   selective-recovery baseline to the proposed confirmatory design.
4. Preserve pre-specified negative controls in which EffectGuard ties or loses.
5. Have a statistical reviewer validate the template-level primary analysis,
   missing-data rule, and safety gate before preregistration.

## Recommendation

Proceed to external scientific review only with the narrowed policy/framework
claim and the falsifiable research question in
`P4_FINAL_RESEARCH_QUESTION_CANDIDATE.md`. Do not freeze the preregistration
or run confirmatory evaluation until reviewers assess the novelty boundary and
the baseline/benchmark provenance requirements.

## Classification Rationale

The challenge does not fail completely because the explicit, auditable
provider-receipt and `UNKNOWN` policy can be studied as a reusable framework.
However, it does not pass as a novel algorithm because RETRO and a
capability-complete Temporal application substantially cover the proposed
mechanism. The contribution must therefore be narrowed before external review.
