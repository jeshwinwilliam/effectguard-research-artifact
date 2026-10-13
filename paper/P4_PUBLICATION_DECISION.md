# P4 Publication Decision

## Selected Option

**B. Narrow to an evaluation-framework or empirical-study paper.**

The primary claim should be that EffectGuard provides a candidate framework for
specifying, executing, and independently evaluating recovery-policy tradeoffs
under ambiguous external effects. The `UNKNOWN` policy is an evaluated policy,
not a claimed novel recovery algorithm.

## Why This Is Stronger Than the Alternatives

| Option | Decision | Reason |
| --- | --- | --- |
| A. Proceed as a full new-recovery-algorithm paper | Rejected | RETRO already provides semantic predicates, dependency tracking, selective re-execution, and external-effect handling; a capability-complete Temporal application can implement the proposed policy. |
| B. Evaluation-framework or empirical-study paper | Selected, conditional | It aligns with the repository's strongest potential asset: explicit receipt/capability contracts, evaluator isolation, negative controls, reproducibility artifacts, and transparent terminal outcomes. Its novelty still requires independent benchmark validation. |
| C. Workshop or tool/demo publication | Retain as fallback | Appropriate if independent curation or a fair strong-baseline study is unavailable. It supports dissemination without overstating research confirmation. |
| D. Redesign before any work | Not selected now | A coherent, falsifiable framework question remains. Redesign becomes necessary if reviewers find the evaluation abstraction redundant or cannot validate independent benchmark semantics. |

## Publication Claim Ceiling

Before external validation, the manuscript may claim only that the repository
contains a proposed, reproducible evaluation framework and safety-policy
specification with exploratory evidence and documented counterexamples. It may
not claim a new recovery algorithm, superior recovery, broad safety, or
independent validation.

## Exact Remaining Scientific Blockers

1. Independent judgment that the receipt/capability abstraction and UNKNOWN
   policy are differentiated from RETRO-style pause/escalation and existing
   workflow/agent evaluation frameworks.
2. Curator-sealed held-out workflow templates, effect annotations, fault
   schedules, final invariants, and hidden outcome truth.
3. Capability-matched Temporal and RETRO-like policy baselines under identical
   provider observations, IDs, deadlines, and compensations.
4. A frozen template-level statistical protocol with power/sensitivity
   rationale, missing-data rules, multiple-comparison policy, and safety gate.
5. A confirmatory result that reports both policy benefits and negative
   controls, including any safety failure or baseline win.

## Next Decision Gate

Request external correctness, benchmark, and statistical review. If those
reviewers approve a distinct evaluation abstraction and a curator can supply
the sealed material, prepare the minimum publishable study. If either gate
fails, choose the workshop/tool route or retire the research claim rather than
conducting a larger self-authored benchmark.

## No Protocol Freeze

This document does not freeze a protocol, authorize an experiment, or alter
historical evidence. It records a publication direction pending independent
validation.
