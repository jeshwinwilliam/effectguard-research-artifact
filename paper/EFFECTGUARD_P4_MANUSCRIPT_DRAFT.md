# EffectGuard: UNKNOWN-Safe Selective Recovery for Agent Workflows with Ambiguous External Effects

## Draft Status

This is a working research manuscript draft. The P4 development-pilot results
below are exploratory deterministic mechanism checks, not confirmatory
evidence. Historical P3 observations remain preliminary diagnostic evidence,
not evidence of correctness, generalization, or statistical advantage.
The one provider-audited service-backed retry/lost-acknowledgement witness is
also development-only; it does not establish restart tolerance, broad fault
coverage, baseline superiority, or algorithmic novelty.

## Empirical Scope

The manuscript is engineering research supported by exploratory deterministic
simulation and integration checks. It is not yet a completed benchmarking
study, a calibrated real-world simulation, or a confirmatory experiment. This
distinction governs all results and limits claims to mechanism feasibility,
specified safety behavior under stated assumptions, and documented failure
modes.

## Contribution Position

The current paper direction is a conditional evaluation-framework and
policy-study contribution: a receipt/capability contract, an explicit
`VALID`/`INVALID`/`UNKNOWN` policy, evaluator isolation, and reproducible
negative controls for ambiguous external-tool outcomes. It does not claim a
new semantic selective-recovery algorithm. A full-paper claim depends on
independently curated workflow semantics, capability-matched Temporal and
RETRO-like baselines, and a sealed confirmatory evaluation.

## Abstract

AI-agent workflows increasingly invoke external systems whose effects may be
ambiguous after timeouts, delayed visibility, crashes, and partial failures.
Recovering such workflows is difficult because preserving too much work can
retain invalid decisions, while replaying too much work can duplicate external
effects. EffectGuard investigates UNKNOWN-safe, invariant-aware selective
recovery. The proposed protocol records logical operation identifiers and
effect receipts, classifies action validity from runtime-visible evidence, and
blocks conflicting irreversible operations while relevant effects remain
UNKNOWN. A separate evaluator validates final invariants without supplying
hidden truth to the runtime. This paper will test whether the protocol can
reduce unnecessary recovery work relative to dependency-only and blocking
baselines without permitting unsafe recovered states.

## Problem Statement

A tool call can commit externally even when the workflow observes a timeout or
UNKNOWN result. A subsequent agent decision may create a conflicting fallback
effect. Existing recovery choices such as restart, checkpoint replay, and
compensation do not by themselves decide whether later work remains
semantically valid under ambiguous evidence.

## Introduction

The central failure is not simply an unsuccessful tool invocation. A workflow
may observe a timeout after a provider accepted a request, then make a fallback
decision that conflicts with the original effect. Conversely, a broad restart
can duplicate a costly or irreversible operation. EffectGuard frames recovery
as an evidence problem: which prior decisions remain justified by receipts the
runtime can actually observe? Its proposed decision layer is designed to work
alongside durable orchestration, idempotency, and compensation, not replace
them. Whether it provides a distinct research contribution remains open.

## Motivation

P3 produced a reproducible diagnostic counterexample: an UNKNOWN cloud
capacity observation could permit a fallback job submission before a delayed
success resolved, leaving conflicting submitted jobs while the run was marked
successful. P3 also exposed an evaluation-circularity risk when a runtime
selection predicate and semantic oracle shared the same domain method. These
findings motivate a safety-first protocol and independent evaluation boundary.

## System Model

Each workflow action has a logical operation identifier, effect class,
dependency and conflict relations, provider capability declaration, and effect
receipt. The runtime distinguishes observed `SUCCESS`, `FAILURE`, and
`UNKNOWN` states. Validity is three-valued: `VALID`, `INVALID`, or `UNKNOWN`.
Only `VALID` actions can be preserved; `UNKNOWN` actions are deferred.

## Proposed Protocol

EffectGuard records receipts, derives a dynamic evidence basis for each
action, blocks irreversible actions in an UNKNOWN conflict cone, selects only
certified invalid actions for recovery, and requires final invariant validation
before reporting `RECOVERED`. Possible terminal outcomes include `BLOCKED`,
`UNRESOLVED`, `RECOVERY_UNSUPPORTED`, `FAILED`, and `UNSAFE`.

## Recovery Protocol

For an `UNKNOWN` receipt, the runtime records the stable logical identity and
the currently available evidence, derives dependency and conflict cones, and
issues `VALID`, `INVALID`, or `UNKNOWN` certificates for affected actions.
Only `VALID` work may be preserved. `INVALID` work needs a declared,
capability-appropriate repair. `UNKNOWN` work is deferred, and irreversible
work in a relevant cone is blocked. Provider verification, idempotency lookup,
or observed compensation evidence may resolve ambiguity; a deadline produces
`UNRESOLVED`, never guessed success.

`RECOVERED` requires successful repair and final invariant validation. The
evaluator owns benchmark-only truth after execution and is not an input to
runtime selection. These properties remain conditional on durable logical IDs,
trustworthy verification, explicit capabilities, and checkable invariants.

## Implementation Architecture

The P4 prototype separates a runtime planner, effect-receipt ledger, and
post-execution evaluator. The runtime produces three-valued validity
certificates from observed receipts and declared provider capabilities; it
does not receive benchmark truth. The evaluator consumes serialized decisions
and fixture-only expected validity and invariant results after execution. A
deliberately incorrect runtime estimator is detected by the evaluator test.
This is architectural separation, not a claim that the evaluator was
independently authored.

The prototype also maintains stable logical operation identifiers and an
in-memory deduplication boundary. This is a development limitation, not
durable provider storage or proof of deployed exactly-once behavior.

Sprint 3B adds a local durable research adapter. Recovery-visible receipts are
stored atomically in SQLite with an append-only transition record, while a
separate SQLite-backed local provider owns authoritative external-effect state.
The recovery runtime cannot import the provider or evaluator-side invariant
suite. This improves crash/restart and adversarial-test realism, but remains a
local adapter rather than a third-party service integration.

## Implementation

The implementation contains deterministic planning, receipt persistence, a
local provider with public submit/resolve/verify/compensate operations,
evaluator-side invariant checks, and adversarial conformance tests. The P4
receipt ledger and provider use separate SQLite stores so runtime code does
not read evaluator truth. This is architectural separation, not independent
implementation or deployed-service evidence.

The Temporal Java baseline uses the official SDK. Sprint 3E also ran it
against an official local Temporal development server with persistent local
state and the P4 provider's HTTP contract. It exercised retry, verification,
compensation, unsupported recovery, and a paused workflow that completed after
a controlled service restart. These are feasibility checks, not production
durability or comparative-performance evidence.

## Development Benchmark Methodology

The versioned P4 development benchmark contains 12 deterministic,
Codex-authored workflows across procurement, travel, cloud, and fulfillment.
It includes delayed success and failure, evidence expiry, UNKNOWN irreversible
effects, duplicate delivery, compensation failure, restart interruption, and
positive and zero semantic-gap controls. Each declared gap label is checked
against the P4 dynamic graph before execution. The suite is development-only
and excluded from independently authored held-out evaluation.

Baselines are blocking, restart, checkpoint/replay, dynamic dependency-only,
Saga-style compensation, idempotency-aware replay, and EffectGuard. They see
the same public receipts, graph, declared capabilities, and invariants. They
are transparent deterministic models, not durable workflow or cloud-service
integrations; they cannot establish a production-baseline comparison.

## Exploratory Development Pilot

An initial 84-run deterministic development pilot exposed an unfair
checkpoint/idempotency baseline model under restart interruption. The raw
artifact is preserved and an amendment documents the correction. A separate,
unpooled corrected 84-run pilot has 65 `RECOVERED`, 7 `UNRESOLVED`, 6
`RECOVERY_UNSUPPORTED`, 4 `FAILED`, and 2 `UNSAFE` outcomes, with no evaluator
failures. The unsafe cases are the intentionally non-idempotent plain restart
baseline under duplicate delivery; the failures include compensation failures
and an interrupted plain restart. These observations preserve negative results
but are not statistical or comparative evidence.

## Preliminary Evaluation

The preliminary record is deliberately diagnostic. P3 exposed delayed-success
and conflicting-fallback behavior plus evaluator/runtime circularity risk. P4
tests exercise UNKNOWN barriers, duplicate delivery, compensation failure,
evidence expiry, unsupported irreversible recovery, and restart interruption.
The corrected 84-row development pilot retains failures and unsafe outcomes;
it is not pooled with P3 or used as a confirmatory estimate. The service-backed
Temporal check establishes integration feasibility only, not a safety rate,
work reduction, or advantage over EffectGuard.

## Safety Assumptions

The protocol relies on durable logical identifiers, trustworthy provider
verification where declared, explicit idempotency and compensation capability
metadata, and independently checkable workflow invariants. It does not claim
that unavailable provider capabilities can be simulated away.

## Research Questions

- Can UNKNOWN-safe recovery avoid incorrect recovered outcomes under delayed
  and duplicate external effects?
- Can evidence-aware selection reduce recovery work compared with dynamic
  dependency-only recovery on genuinely positive semantic-gap workflows?
- Does the safety and selectivity behavior generalize across independently
  authored workflow templates and domains?

## Evidence Status and Evaluation Plan

The current evidence is limited to deterministic, Codex-authored development
workflows. A corrected 84-run development pilot preserved all raw traces and
reported no `RECOVERED` result with a failed modeled final invariant. It also
retained negative results from compensation failure, interruption, duplicate
delivery, evidence timeout, and unsupported irreversible recovery. These are
implementation checks, not confirmatory evidence of safety, selectivity,
generalization, or comparative performance.

A confirmatory study remains pending. It must use independently authored and
sealed workflow templates, an evaluator isolated from runtime predicates, a
durable receipt adapter, fair baseline implementations, and a frozen analysis
plan. The independent workflow template, rather than a repeated random seed,
will be the primary unit of analysis. A safety gate will precede any
selective-recovery comparison: a recovered workflow that fails an independent
final invariant invalidates a performance claim.

## Reproducibility Plan

The repository preserves separate pre-correction and corrected development
pilot namespaces, raw trace per workflow/strategy pair, manifests, benchmark
configuration, and offline tests. A future confirmatory package must add
immutable task/evaluator contracts, provider evidence, durable receipt-store
records, environment digests, excluded rows, failure taxonomy, and scripts
that reproduce every table and figure. Historical P3 evidence will remain
separate and will not be pooled with P4 observations.

## Reproducibility and Review Plan

Before confirmatory execution, the project requires a curator-sealed external
benchmark, hidden evaluator, versioned provider and fault contracts, paired
baseline configurations, environment digests, and a frozen analysis plan.
Independent reviewers are being asked to assess correctness assumptions,
benchmark provenance and annotation legitimacy, and statistical methodology.
No reviewer feedback has been received at the time of this draft.

## Related Work

Long-lived transaction recovery and compensation are well established. Sagas
decompose long-running work into actions and compensating actions
[@garciamolina1987sagas], while Beldi provides fault-tolerant and transactional
stateful serverless workflows through logging and transaction protocols
[@zhang2020beldi]. Provider idempotency tokens are likewise established
practice for making retries safe when a provider durably binds a client request
identifier to an operation [@featonby2021idempotency]. EffectGuard does not
claim any of these mechanisms as new.

Semantic dependency reasoning also has direct predecessors. Workflow systems
can validate and infer fine-grained data-dependency annotations
[@bowers2018dependency]. More importantly, RETRO records an action history
graph, uses semantic predicates to refine affected actions, selectively
re-executes them, and uses compensation for external effects
[@kim2010retro]. RETRO is therefore the strongest challenge to any claim that
EffectGuard introduces semantic selective recovery. The contribution, if one
is ultimately supported, must be limited to a tested policy and interface for
agent workflows: runtime-visible receipt evidence, an explicit
`VALID`/`INVALID`/`UNKNOWN` decision, conflict-cone blocking for irreversible
work, and a separate final-state evaluator.

Durable orchestration supplies an important comparison boundary. Temporal
persists a workflow event history and replays it to reconstruct state after
worker failure [@temporalEventHistory]. Its applications can implement
domain-specific validity, reconciliation, and `UNKNOWN` policies, so this
paper does not claim those capabilities are unavailable to Temporal. The
proper comparison is between paired policy configurations with equivalent
provider verification, idempotency, compensation, and external observations,
not between a durable platform and a simplified local replay model.

Existing workflow and agent research also informs evaluation design. WfCommons
offers externally authored scientific-workflow topology
[@coleman2022wfcommons], but it does not provide EffectGuard-specific effect
annotations or sealed external-effect truth. Recent tool-using-agent work
evaluates robustness under tool faults [@lewandowska2026robustness], supporting
the relevance of fault injection without validating this protocol's safety or
novelty. Accordingly, independently curated effect contracts, hidden
evaluation truth, and a source-complete review of recent agent-recovery work
remain prerequisites for a confirmatory claim.

The paper will not describe its local checkpoint/replay model as Temporal or
another production durable-workflow engine. Sprint 3E added a small
service-backed development integration using the official Temporal CLI local
development server, the Temporal Java SDK, a persisted local server database,
and the P4 provider's public HTTP contract. It demonstrated Activity retry,
provider-visible logical IDs, ambiguous-outcome verification, compensation,
unsupported recovery, and persistence of one paused Workflow across a
controlled server restart. This is integration evidence only: it does not
establish production durability, comparative performance, independent
validation, or superiority.

A fair claim against durable orchestration still requires an independently
reviewed, paired experiment with one sealed fault schedule, provider contract,
time budget, and final-state evaluator. Temporal's native retry and durable
history must be distinguished from any externally supplied semantic-validity
policy. Until those conditions hold, durable systems remain related work and
experimental claims are limited to the explicitly labeled development
strategies.

## Related-Work Boundary

Durable workflow engines provide persisted event history and replay across
crashes [@temporalEventHistory]; provider-side idempotency constrains duplicate
effects [@featonby2021idempotency]; and Saga patterns coordinate compensations
[@garciamolina1987sagas]. EffectGuard does not replace these mechanisms. Its
proposed boundary is deciding when later work is safe to preserve after an
ambiguous external effect and when the correct answer is to block, remain
unresolved, or report recovery unsupported. This distinction requires a
complete, source-verified literature review before any novelty claim or venue
decision.

Classic Sagas establish compensation for long-lived transactions; durable
workflow platforms persist history and replay across crashes; and idempotency
keys constrain repeated external effects. The proposed contribution is not any
of these mechanisms in isolation. It is the still-unverified claim that
evidence-aware semantic preservation supplies a conservative decision layer
when external outcomes remain ambiguous. A held-out study must compare against
faithful implementations before this distinction can be described as novel.

Source review currently supports only this narrow boundary. Sagas establish
compensation; durable engines record/replay execution history; idempotency
constrains duplicate effects when a provider supports it; and workflow systems
already expose retries and error states. EffectGuard must therefore show,
rather than assume, that explicit `UNKNOWN` validity certificates and
conflict-cone blocking add a distinct measured benefit. The strongest
counterargument is that these behaviors are an application-level composition
of established durability, reconciliation, provenance, and compensation
patterns. Novelty remains unresolved pending a peer-reviewed semantic-recovery
and agent-tool-recovery review.

## External Benchmark and Review Gate

No ready-made public benchmark provides both independent workflow structure
and sealed external-effect truth. WfCommons is a promising source of workflow
topology [@coleman2022wfcommons] but lacks provider-effect contracts; WorkflowHub entries have
workflow-specific licensing; and declarative workflow examples provide
controls rather than outcome benchmarks. A separate curator must select
version-pinned sources, verify licenses, author effect contracts and
invariants, and retain the fault/evaluator package separately from the
implementers. An external reviewer must assess the formal safety specification,
UNKNOWN transitions, receipt persistence assumptions, evaluator isolation, and
baseline fairness. Until those reviews occur, no confirmatory run or
preregistration freeze is justified.

## Development-Only External Topology and Temporal Prototype

Sprint 3D adds two small public WfCommons Montage execution instances as an
externally authored source of workflow topology. The importer validates their
WfFormat task graph, while all provider effects, capabilities, UNKNOWN policy,
and final invariants remain in a separate EffectGuard-authored synthetic
overlay. The adaptation is therefore useful for development integration but is
not independently authored external-effect evidence.

Sprint 3D also adds a Java baseline using the official Temporal SDK. The
prototype executes a Workflow and retried Activities through Temporal's SDK
test service, uses a stable idempotency key, verifies an ambiguous receipt, and
models explicit compensation. The test-service result is not evidence of an
external Temporal deployment or crash-persistent history. A faithful
comparative claim requires a version-pinned external service and a shared
provider contract under paired faults.

The four-strategy Sprint 3D development comparison records terminal safety
behavior only. All rows recover under their modeled contracts; it reports no
timing, workload, generalization, or superiority result. Its purpose is to
preserve integration limitations before a later sealed study, not to replace
independent validation.

## Threats to Validity

The current mechanism is deterministic and its provider adapter is local.
Independent benchmark authorship, external reviewer feedback, a faithful
durable-workflow baseline or narrowed comparison claim, a peer-reviewed
novelty review, model nondeterminism, external-service variability, and full
P1/P4 executor conformance remain future work. The evaluator is structurally
separate but not independently authored. Historical P3 artifacts and
development-pilot variants remain limited preliminary evidence and will not be
pooled with P4 confirmatory observations.

## Ethical and Operational Considerations

The motivating failure can create duplicate purchases, conflicting resource
allocations, or other harmful external effects. A false positive recovery may
hide such harm; excessive blocking can impose availability costs. The protocol
therefore favors explicit `BLOCKED`, `UNRESOLVED`, and
`RECOVERY_UNSUPPORTED` outcomes over unjustified success. A future benchmark
must also prevent evaluator leakage and disclose external-service, cost, or
data-handling risk. These choices reduce risk but do not establish operational
safety outside the stated assumptions.
