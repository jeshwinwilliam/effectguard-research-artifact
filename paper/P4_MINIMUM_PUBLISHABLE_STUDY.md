# P4 Minimum Publishable Study

## Goal

The smallest study that could support a full evaluation-framework/policy paper
must test whether the framework yields credible, fair, and reproducible
evidence. It is not a minimum number of runs alone.

## Indispensable Requirements

| Requirement | Minimum acceptable form | Why indispensable |
| --- | --- | --- |
| Independent workflow provenance | A curator selects or authors a sealed held-out set from public, licensed workflow sources; EffectGuard developers do not see outcomes before freeze. | Prevents policy-tailored workflows and establishes external validity. |
| Independent effect annotations and invariants | A domain/benchmark curator authors or approves effect contracts, semantic dependencies, conflicts, and final invariants; provenance is recorded. | Topology alone cannot validate EffectGuard-authored external-effect semantics. |
| Independent correctness assessment | A distributed-systems reviewer checks assumptions, terminal truth table, UNKNOWN transitions, and evaluator information boundaries. | The safety interpretation cannot be self-certified. |
| Capability-matched strong baselines | Temporal durable replay and a RETRO-like semantic policy receive the same IDs, verification, idempotency, compensation, graph, faults, deadline, and evaluator. | Rules out an advantage caused by withholding capabilities from a baseline. |
| Positive and negative controls | Include duplicate-safe timeout, semantic preservation, irreversible ambiguous conflict, unsupported recovery, and a case where a strong baseline ties or wins. | Tests both intended behavior and benchmark bias. |
| Statistical protocol | Template-level paired analysis; safety co-primary endpoint; pre-specified missing-data, provider-failure, multiplicity, and stopping rules. | Repeated seeds cannot replace independent templates. |
| Reproducible artifact | Versioned tasks, prompts/tool contracts where applicable, environment digests, raw immutable rows/traces, manifests, analysis scripts, tables, figures, and failure taxonomy. | Lets reviewers reproduce both positive and negative conclusions. |

## Optional but Valuable Enhancements

- Multiple real provider integrations or a production-like third-party service.
- Multiple agent models and model seeds.
- Larger workflow corpus, more domains, and longitudinal provider failures.
- A mechanized proof of selected safety invariants.
- A broader baseline set beyond Temporal and RETRO-like semantic recovery.

These strengthen generality but cannot substitute for independence or fairness.

## Minimum Design

1. Curate enough independent templates to make template-level uncertainty
   estimable; choose the count through a pre-study sensitivity analysis rather
   than selecting it after observing effects.
2. For every template, execute all policy arms under the same public provider
   behavior and fault schedule. Preserve incomplete groups and do not selectively
   rerun unfavorable outcomes.
3. Treat final-invariant failure after `RECOVERED` as a safety-gate failure that
   prevents a performance/superiority conclusion.
4. Report recovery work, selection precision/recall where a sealed affected-set
   oracle exists, and availability costs (`BLOCKED`, `UNRESOLVED`, unsupported,
   and latency) together.
5. Publish the sealed material only after evaluation, with enough detail for
   an independent rerun.

## Evidence the Existing Repository Already Supplies

- A candidate terminal-state and UNKNOWN specification.
- Deterministic local-provider and evaluator separation tests.
- A service-backed Temporal feasibility prototype.
- Raw P3 artifacts and a complete but mixed P3-C9 report.
- A reproducibility and reporting structure.

## Evidence the Existing Repository Does Not Supply

- Independently authored/sealed effect semantics and ground truth.
- An independently reviewed correctness argument.
- A capability-matched Temporal policy comparison.
- A RETRO-like semantic baseline.
- Generalizable template-level inference.

## Stop Rule

If a curator cannot provide independent annotations/hidden outcomes, or if the
strong baselines cannot be implemented fairly, do not run a confirmatory study
as a full-paper evaluation. Reposition as a workshop/tool artifact instead.
