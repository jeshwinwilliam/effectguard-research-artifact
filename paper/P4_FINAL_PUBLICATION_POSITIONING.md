# P4 Final Publication Positioning

## Evidence Boundary

The record supports feasibility and failure analysis, not a confirmed recovery
algorithm or general safety claim.

- **Verified operational evidence:** P3-C9 completed 100 paired runs with
  complete groups and preserved raw artifacts. Its semantic-gap subset favored
  EffectGuard over `dependency_only` in travel but tied in procurement. All
  nonblocking strategies, including EffectGuard, produced incorrect outcomes in
  the S9 UNKNOWN cloud controls. This is mixed evidence, not a novelty result.
- **Verified development evidence:** P4 specifies terminal safety semantics,
  exercises deterministic behavior and local-provider contracts, and has a
  service-backed Temporal feasibility check. It is not independently curated,
  sealed, or confirmatory.
- **Unsupported claims:** broad safety, algorithmic novelty, superiority over
  durable workflow systems, independent validation, and general agent-workflow
  applicability.

## Candidate Publication Directions

| Direction | Novelty potential | Strongest overlap | Evidence still required | Main reviewer objection | Current feasibility | Full-paper suitability |
| --- | --- | --- | --- | --- | --- | --- |
| A. UNKNOWN-safe recovery specification and verification | Conditional. Explicit terminal-state and receipt rules are useful only if they impose properties not already captured by established recovery policies. | RETRO's semantic selective re-execution and external-dependency handling; Saga compensation; application-defined Temporal policies. | Independent correctness review, a formalization precise enough for mechanical checking or a convincing proof, and evidence the policy boundary is not merely RETRO-style pause/escalation. | “This is a familiar conservative recovery policy expressed with new labels.” | Moderate engineering readiness; insufficient scientific differentiation. | Weak as the sole contribution today. |
| B. Reproducible evaluation framework for ambiguous external effects | Conditional but currently strongest. A reusable receipt/capability contract, hidden-truth evaluator boundary, negative controls, and paired baseline harness could fill an evaluation-method gap. | Existing workflow, agent robustness, fault-injection, and durable-execution benchmark frameworks. | Independent benchmark provenance, curator-sealed annotations/outcomes, fair Temporal and RETRO-like policies, reusable artifact packaging, and external reviewer judgment that the benchmark abstraction is valuable. | “The framework is synthetic, tailored to the proposed policy, or merely a test harness.” | Strongest fit with existing P4 artifacts, but independence is missing. | Plausible full software-engineering paper only after independent curation and evaluation. |
| C. Empirical characterization of recovery-policy tradeoffs | Potentially useful if framed as negative/conditional evidence, not superiority. | Prior recovery evaluations, RETRO, durable workflow benchmarks, and agent fault-injection studies. | Multiple independently authored templates, cluster-aware analysis, fair baselines, positive and negative controls, replicated provider/fault conditions, and transparent incomplete/failure rules. | “Small synthetic benchmark and one model/provider cannot support a general characterization.” | P3 offers a diagnostic starting point; not enough for a paper. | Plausible only after the minimum study below. |

## Chosen Position

Choose **B: narrow to an evaluation-framework and policy-study paper**, with
the UNKNOWN-safe policy treated as the object of evaluation rather than as a
claimed new algorithm. Direction C is a supporting result section if the
minimum study produces meaningful, mixed, or negative tradeoffs. Direction A
should remain a specification artifact and correctness precondition, not the
headline novelty claim.

This choice is stronger than an algorithm paper because RETRO already supports
semantic predicates, dependency tracking, selective re-execution, and external
effect handling. It is stronger than a tool/demo-only submission if independent
curation turns the framework into reusable evaluation infrastructure rather
than a project-specific test suite. It is weaker than a full systems claim and
must be withdrawn if the independent study finds no abstraction or evaluation
value beyond existing frameworks.

## Venue Positioning

| Venue class | Fit under the chosen position | Preconditions and cautions |
| --- | --- | --- |
| ICSE or FSE research track | Possible only with independent benchmark provenance, strong related-work differentiation, sound template-level analysis, and a substantive reusable artifact. | Do not submit a deterministic local prototype plus P3 evidence as a general recovery-systems paper. |
| ICDCS | Possible if the focus becomes distributed external-effect semantics, provider contracts, and durable-policy comparison. | Requires stronger distributed-systems evaluation and a fair production-like baseline than currently exists. |
| Software engineering or distributed systems journal | Better suited to a mature, extended artifact and multi-stage empirical study. | Not an immediate target; journal scope does not remove independence or novelty requirements. |
| Workshop or tool/demo track | Most appropriate current fallback if the external benchmark or confirmatory study cannot be completed. | Present the framework, specification, known S9 failure, and open evaluation challenge; do not claim confirmed novelty. |

## Decision

Proceed toward a **full evaluation-framework/policy-study paper only
conditionally**. If external curation and fair evaluation cannot be obtained,
target a workshop/tool demonstration or redesign/retire the research claim
rather than inflating the existing evidence.
