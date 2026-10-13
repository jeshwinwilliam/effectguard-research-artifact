# P4 Independent Benchmark Curation Protocol

## Status

This is a proposed curation protocol. It does not select a benchmark, create
hidden outcomes, authorize a study, or freeze a preregistration.

## Roles and Independence

| Role | Permitted work | Prohibited work |
| --- | --- | --- |
| EffectGuard developers | Provide importer, schema, public baseline interface, reproducibility tooling, and documented assumptions. | Selecting held-out outcomes, editing curator annotations after observing results, or accessing hidden evaluator truth. |
| Independent curator | Select templates, record provenance/license, author or approve effect annotations, define faults/invariants, and retain the sealed evaluator. | Co-developing a policy arm or changing labels to favor a strategy. |
| Correctness reviewer | Assess assumptions, transition rules, invariants, and information boundaries. | Approving a safety claim solely from developer tests. |
| Statistical reviewer | Approve unit, analysis, multiplicity, attrition, and stopping plan before outcomes are visible. | Selecting tests or thresholds after results. |

Independence requires disclosure of affiliations, prior collaboration, funding,
and any role in EffectGuard development. A curator or reviewer with a material
conflict must be replaced or the limitation disclosed and the study narrowed.

## Workflow Selection Criteria

Include a version-pinned, licensed, externally authored workflow only when it:

1. Is a valid DAG or has a declared, supported control-flow representation.
2. Has enough task-level structure to express at least one potential semantic
   dependency and one unaffected branch.
3. Can be adapted to a public tool/effect interface without inferring real
   financial, medical, or irreversible effects from task names alone.
4. Can support a curator-defined final invariant and observable provider state.
5. Has a license permitting the planned transformation, redistribution, and
   artifact release.
6. Is distinct from any development template used to design EffectGuard policy
   or tune a baseline.

Exclude malformed graphs, undocumented licenses, templates whose annotations
would require fabricated domain facts, and workflows that cannot support a
sealed final-state evaluator.

## Annotation Package

For each selected template, the curator must produce a versioned annotation
package separate from the unmodified source topology. Each effect annotation
must state:

- effect type and provider interface;
- logical operation-ID and idempotency behavior;
- reversibility and compensation capability;
- authoritative verification capability and evidence delay model;
- dependency and conflict relations, with rationale;
- `UNKNOWN` transition conditions and permitted terminal outcomes;
- final safety invariants and liveness/termination expectations;
- provenance source, curator rationale, and synthetic-versus-supported status.

The package must identify which annotations are synthetic overlays. Synthetic
does not mean invalid, but it cannot be described as independently observed
real-world effect semantics.

## Hidden Outcome Truth

The curator owns the fault schedule, authoritative provider-state trajectory,
and final evaluator. During study execution, each runtime can observe only the
public provider contract, declared capabilities, and its own receipts. It must
not receive the hidden affected set, final invariant result, future provider
state, or another strategy's trace.

The sealed evaluator should emit, after a run completes, a signed or hashed
record of final-state invariants, logical-effect uniqueness, required
compensations, and the affected-set oracle where that metric is applicable.

## Safety, Liveness, and Controls

Every benchmark suite must include:

- a duplicate-safe timeout control where all capability-matched strategies can
  recover safely;
- a semantic-preservation control where a RETRO-like policy can preserve an
  unaffected branch;
- an irreversible ambiguous-conflict control where unsafe fallback is blocked;
- an unsupported-recovery control where safe systems must not claim success;
- at least one scenario where a strong baseline ties or outperforms EffectGuard.

Safety means no `RECOVERED` result violates a sealed final invariant. Liveness
is conditional: when evidence resolves and declared capabilities are available,
the policy should reach a truthful terminal status. A system is not penalized
for returning `BLOCKED`, `UNRESOLVED`, or `RECOVERY_UNSUPPORTED` when evidence
or capability is genuinely unavailable; those outcomes are reported as
availability costs.

## Leakage Prevention

1. Store topology, public annotations, and sealed truth in separate access
   domains.
2. Hash and version every public contract before any run.
3. Do not expose expected affected sets, invariant verdicts, or future fault
   transitions through prompts, fixture names, logs, error strings, or metrics.
4. Run baseline arms with identical public initial state and fault schedule.
5. Record access logs and manifest digests for curator materials.
6. Do not revise templates, labels, or exclusion decisions after viewing arm
   outcomes; any amendment starts a new study version.

## Exclusion and Withdrawal Rules

Before execution, exclude a template only for a documented licensing,
malformation, unsupported-control-flow, safety, or unresolvable annotation
reason. After execution begins, retain rows unless an independently documented
infrastructure failure makes every paired arm unavailable. Report exclusions,
incomplete groups, and provider failures in the final artifact; never replace
unfavorable rows selectively.

## Required Release Package

Release after the study: original topology plus license/provenance, public
annotation schema, sealed-material release policy, environment digest, run
manifest, raw immutable traces, analysis code, all terminal statuses, and a
failure taxonomy. Release hidden truth only when it no longer compromises a
planned replication or with the curator's documented timing decision.
