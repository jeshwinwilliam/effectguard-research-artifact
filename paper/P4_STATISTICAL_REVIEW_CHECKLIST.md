# P4 Statistical Review Checklist

## Scope

This checklist requests review of a future confirmatory design. It does not
freeze thresholds, calculate sample size from development outcomes, or approve
an experiment.

## Research Question and Estimands

| Item | Proposed requirement | Reviewer decision |
| --- | --- | --- |
| Primary question | Does the independently curated framework expose safety, selectivity, and availability tradeoffs among capability-matched recovery policies? | APPROVE / REVISE / BLOCK |
| Primary unit | Independently authored workflow template, with paired strategy executions nested within template. Seeds and attempts are repeated measurements, not independent templates. | APPROVE / REVISE / BLOCK |
| Co-primary safety endpoint | Proportion of `RECOVERED` runs with all sealed final invariants true; any unsafe recovered outcome invokes the safety gate. | APPROVE / REVISE / BLOCK |
| Policy-effect endpoints | Recovery work, selection precision/recall where a sealed affected-set oracle exists, and availability cost (`BLOCKED`, `UNRESOLVED`, unsupported, failure, latency). | APPROVE / REVISE / BLOCK |
| Directionality | Two-sided comparisons unless a safety gate makes a claim logically impossible. | APPROVE / REVISE / BLOCK |

## Paired Design and Analysis

1. Each template/fault schedule forms a pairing group containing every required
   arm and identical public provider observations.
2. Analyze paired differences at the template level; use cluster-aware methods
   or hierarchical models when multiple schedules/seeds belong to a template.
3. Report effect sizes and confidence intervals, not only p-values.
4. Use bootstrap or permutation intervals only with a documented resampling
   unit that respects template clusters.
5. Pre-specify the contrast family: EffectGuard versus capability-matched
   Temporal, RETRO-inspired semantic recovery, and diagnostic weaker arms.
6. Control family-wise error or false-discovery rate across non-primary
   contrasts, or label them exploratory. The chosen method must be approved
   before sealed outcomes are revealed.

## Missing Data and Failure Policy

| Event | Required treatment |
| --- | --- |
| One arm missing in a paired group | Preserve raw row and classify group incomplete. Exclude it only from paired estimands under a pre-specified rule; report attrition by arm and cause. |
| Provider/authentication/quota failure | Preserve as operational evidence; do not selectively retry. Follow a frozen retry budget and state whether the group is incomplete. |
| Evaluator failure | Treat as a study-integrity incident. Do not substitute runtime output for evaluator truth. |
| Invalid benchmark annotation | Quarantine only under curator-approved, pre-specified criteria; retain provenance and explain whether all paired rows are withdrawn. |
| Unsafe `RECOVERED` terminal | Retain, report, and invoke the safety gate. It cannot be removed as an outlier. |

## Stopping and Falsification Rules

- Stop a campaign for a confirmed evaluator leak, unrepairable shared-provider
  defect, or safety-gate violation according to the pre-specified protocol.
- Do not stop early because an apparent EffectGuard advantage appears.
- Do not replace templates or rerun unfavorable strategy rows.
- A meaningful EffectGuard claim is falsified if a strong baseline matches or
  outperforms it on safety, work, and availability under the primary analysis,
  or if a benefit is explained by increased unresolved/blocking outcomes.
- A framework claim is weakened or falsified if independent reviewers find the
  abstraction redundant or curator-sealed labels do not produce reproducible
  strategy comparisons.

## Sample-Size and Sensitivity Review

The statistician must select the number of independent templates through a
prospective sensitivity or power analysis using a substantively meaningful
effect and plausible between-template variation. P3/P4 development effect sizes
must not be used as a favorable empirical basis without explicit sensitivity
qualification. The analysis must state the smallest effect of interest, target
precision, expected attrition, and decision consequences of inconclusive data.

## Reviewer Checklist

- [ ] The estimand distinguishes safety from availability.
- [ ] The independent template, not seed, is the inferential unit.
- [ ] Paired groups are fully defined before outcome access.
- [ ] Intervals and multiplicity treatment are pre-specified.
- [ ] Missing and failed provider rows cannot be selectively removed.
- [ ] The safety gate prevents a performance claim after unsafe recovery.
- [ ] Negative controls and baseline wins are reportable outcomes.
- [ ] The proposed sample-size rationale is prospective and credible.
