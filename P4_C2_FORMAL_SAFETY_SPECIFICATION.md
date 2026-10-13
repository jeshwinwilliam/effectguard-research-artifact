# EffectGuard P4-C2 Formal Safety Specification

## Status and Scope

This document is the Sprint 1 implementation contract for P4. It is based on
the P4-C1 design and the documented P3-C11 discrepancies. It does not change
P3 source, tasks, results, or scientific conclusions. P4 has not yet
established safety, novelty, or generalization; the properties below are
claims to be tested under their stated assumptions.

## Contribution Boundary

P4 studies UNKNOWN-safe, invariant-aware selective recovery for workflow
actions that may interact with ambiguous external effects. It does not claim
exactly-once execution for services that lack idempotency, durable operation
identifiers, status verification, or compensation support.

## State Model

For workflow `W = (A, E, I)`, every action `a` has:

- a stable logical operation identifier `lid(a)`;
- an effect class in `READ_ONLY`, `REVERSIBLE`, `COMPENSATABLE`, or
  `IRREVERSIBLE`;
- observed effect receipts `R(a)`; and
- dependency and conflict relations in the runtime provenance graph `E`.

An effect receipt contains a logical operation identifier, provider reference,
idempotency key where supported, observed state, timestamp, and verification
evidence. The runtime sees only observed state:

`Observed(a) in {SUCCESS, FAILURE, UNKNOWN}`.

The independent evaluator may use benchmark-only hidden truth. Hidden truth is
not passed to the recovery runtime or its validity estimator.

For each action, recovery computes:

`Validity(a) in {VALID, INVALID, UNKNOWN}`.

`UNKNOWN` is not a synonym for `VALID` or `INVALID`. It cannot justify
preservation, compensation, replay, or a successful terminal status.

## Terminal Status Truth Table

| Terminal status | Required condition | Forbidden condition |
| --- | --- | --- |
| `RECOVERED` | All required recovery steps succeeded and final invariants validate. | Any unresolved required evidence or invariant violation. |
| `BLOCKED` | The runtime intentionally withheld unsafe progress while waiting for evidence or intervention. | Treating the partial state as recovered. |
| `UNRESOLVED` | The evidence deadline expired without a decisive safe resolution. | Retrying or guessing merely to force completion. |
| `RECOVERY_UNSUPPORTED` | Safe recovery requires an unavailable provider capability. | Replaying an irreversible effect without a stated guarantee. |
| `FAILED` | An authorized recovery step failed before invariants were established. | Reporting recovery success. |
| `UNSAFE` | Final validation found an invariant violation, duplicate logical effect, or conflicting irreversible effect. | Downgrading the outcome to recovered or blocked. |

A no-op recovery is represented as `RECOVERED` only after final invariant
validation. Status precedence is `UNSAFE`, then `FAILED`, then
`RECOVERY_UNSUPPORTED`, then `UNRESOLVED`, then `BLOCKED`, then `RECOVERED`.

## UNKNOWN Transition Semantics

1. An ambiguous receipt is recorded as `UNKNOWN` under its stable logical ID.
2. The runtime identifies actions causally dependent on, or conflicting with,
   that receipt.
3. Independently valid read-only or reversible work may continue.
4. An irreversible action in the UNKNOWN causal or conflict cone is blocked.
5. The runtime may use only receipt verification, provider status lookup,
   idempotency lookup, or a declared compensation receipt to resolve UNKNOWN.
6. If decisive evidence arrives, validity is recomputed and a new plan is made.
7. If the declared evidence deadline expires, the status is `UNRESOLVED`.

## Irreversible-Effect Constraint

The runtime must not start, replay, or preserve an irreversible action when
its correctness depends on an UNKNOWN effect or it conflicts with a possibly
committed UNKNOWN effect. A duplicate attempt is rejected when the provider
supports logical-ID deduplication; otherwise a required replay becomes
`RECOVERY_UNSUPPORTED`.

## Selective Preservation Rule

An action can be preserved only when the runtime has a validity certificate
containing its evidence basis and a `VALID` result. An action with `UNKNOWN`
validity is deferred. An action with `INVALID` validity is repaired only if
its effect class and provider capability permit a safe recovery operation.

## Safety Properties

| Property | Statement | Evidence required |
| --- | --- | --- |
| S1: Final-state safety | `RECOVERED` implies all declared final invariants hold. | Independent final validation record. |
| S2: UNKNOWN barrier | Conflicting irreversible work cannot proceed while relevant evidence is UNKNOWN. | Provenance, receipt, and decision trace. |
| S3: Logical-effect uniqueness | A logical operation cannot create a second committed external effect when deduplication is available. | Logical ID, idempotency key, and provider receipt. |
| S4: Certified preservation | Preserved actions have `VALID` certificates; UNKNOWN actions are never silently preserved. | Plan certificates and receipt references. |
| S5: Safe termination | Under eventual evidence resolution and available capabilities, execution reaches a truthful terminal status. | Controlled delayed-result tests. |

S5 is conditional. It does not promise eventual successful completion when a
provider cannot verify, compensate, or deduplicate the relevant effect.

## External-Service Assumptions

- Provider references and logical operation IDs are durable for the relevant
  recovery window.
- Idempotency and deduplication are explicitly declared capabilities, not
  inferred from a successful HTTP response.
- Status verification returns a trustworthy observation, or failure remains
  UNKNOWN.
- Compensation is itself observable and can fail.
- Final invariants are supplied by the workflow contract and are independently
  checkable in the benchmark harness.

## S9 Counterexamples

### S9-A: Delayed success with conflicting irreversible fallback

`check_capacity_A` returns UNKNOWN. The agent allocates worker B and attempts
an irreversible `submit_job_B`. The delayed result later reports that capacity
A succeeded. The P4 runtime must block `submit_job_B`; it must not label the
state `RECOVERED` unless exactly one submitted job is independently verified.

### S9-B: Delayed failure with safe fallback

`check_capacity_A` returns UNKNOWN and later resolves to FAILURE. The runtime
may proceed with a new B workflow only after that evidence is recorded. The B
operation must use a fresh logical ID and declared provider capabilities.

### S9-C: Duplicate delivery after restart

The runtime restarts after submitting an irreversible logical operation. A
repeated delivery with the same logical ID must be deduplicated or reported as
`RECOVERY_UNSUPPORTED`; it must never silently issue a second effect.

### S9-D: Compensation failure

An invalid compensatable effect cannot be reversed because compensation fails.
The terminal result must be `FAILED` or `UNSAFE`, never `RECOVERED`.

## P1/P4 Conformance Boundary

Sprint 1 provides a terminal-status adapter and deterministic behavioral
conformance tests for P1-supported outcomes. It does not claim full P1/P4
executor equivalence. Full equivalence requires a shared execution interface,
golden traces, and adapter integration in a later sprint.

## Deliberate Deviations From P4-C1

Sprint 1 uses an in-memory receipt ledger and deterministic provider
capability model. This is a deliberate minimum-viable implementation, not a
durable distributed storage claim. Real provider adapters, held-out benchmarks,
and confirmatory evaluation remain out of scope.
