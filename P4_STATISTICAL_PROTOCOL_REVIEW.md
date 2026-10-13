# EffectGuard P4 Statistical Protocol Review

## Status

This review improves the draft but does not freeze it. Freeze requires an
independently authored/sealed benchmark, provenance review, a statistician,
and a decision on the durable-workflow comparison.

## Unit, Pairing, and Co-Primary Gates

- The independent unit is a workflow template, not an execution, seed, action,
  or trace. Fault variants and repeated seeds are clustered observations.
- Every template/fault/seed group runs every frozen strategy with the same
  interfaces, capabilities, faults, time budget, and retry constraints.
- The provisional target is 60 independent templates across at least five
  domains. It is a sensitivity target, not an approved power calculation.
- **Safety co-primary:** any `RECOVERED` terminal status with an independently
  failed final invariant is a critical event, pauses the campaign, and blocks a
  performance-success claim.
- **Selective-work co-primary:** paired recovery work on positive-gap
  templates against dynamic dependency-only recovery, evaluated only after the
  safety gate passes.

## Metrics and Analysis

Recovery precision is correctly selected evaluator-invalid actions divided by
all selected invalid actions; recall is correctly selected evaluator-invalid
actions divided by all evaluator-invalid actions. Report undefined denominators
as not applicable. Report recovery work, wall-clock/step overhead,
provider-operation count, blocking duration, availability loss, terminal-state
distribution, and positive-gap/zero-gap results separately.

Use template-level aggregation or a hierarchical model with template as the
cluster; seeds never become independent templates. Report effect sizes,
confidence intervals, distributions, and raw template summaries. The two
primary gates are co-primary; use Holm adjustment for the prespecified
secondary endpoint family. Domain/scenario contrasts are descriptive unless
separately powered and frozen.

With zero unsafe outcomes in 60 independent template-fault units, the
one-sided 95% exact binomial upper bound is below 5% (approximately
`1 - 0.05^(1/60)`). A simple normal approximation gives about 80% paired power
near `d_z = 0.36` for 60 pairs. Both calculations need independent
statistician validation for clustering, attrition, and multiplicity.

## Missing Data, Failures, and Stopping

- Persist every attempt, provider failure, timeout, malformed output, receipt,
  and retry in a frozen taxonomy; never retry only unfavorable outcomes.
- Do not impute incomplete pair groups. Exclude them from paired primary
  estimates but retain them as visible attrition.
- `UNKNOWN`, `BLOCKED`, and `RECOVERY_UNSUPPORTED` are conservative terminal
  outcomes, not successes and not missing observations.
- Stop for a recovered invariant violation, evaluator isolation breach,
  benchmark leakage, or systemic provider/baseline failure preventing complete
  pairing. Report incomplete or negative results instead of weakening a rule.

Publish source/manifests, evaluator and configuration digests, raw traces,
exclusions, pairing completeness, scripts, and all negative results.
