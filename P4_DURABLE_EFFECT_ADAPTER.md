# P4 Durable External-Effect Adapter

## Scope

Sprint 3B adds a local research adapter, not a third-party production
integration and not an exactly-once claim. It separates three concerns:

1. `DurableReceiptStore` persists recovery-visible receipts and transition
   history in a SQLite WAL database.
2. `LocalEffectProvider` owns a different SQLite database representing
   authoritative external-effect state.
3. `AuthoritativeInvariantSuite` reads provider state through its public
   interface after execution; the P4 runtime imports neither the provider nor
   the invariant suite.

## Durable Receipt Contract

The receipt store key is `(workflow_id, logical_operation_id)`. Each receipt
records the effect class, observed status, provider reference, idempotency key,
and declared provider capabilities. Writes use an immediate SQLite transaction
with full synchronization. A receipt submission and its audit transition either
commit together or both roll back.

The only decisive transition allowed after `UNKNOWN` is to `SUCCESS` or
`FAILURE`. Contradictory decisive observations are rejected. Duplicate logical
operation IDs are rejected by the database uniqueness constraint. The store
exposes ordered transition history for audit and a deterministic pre-commit
failure injector for crash-boundary tests.

## Local Provider Contract

The provider is intentionally separate from recovery-process storage. It owns
logical operation IDs, idempotency keys, provider references, outcome state,
and compensation state. It supports:

- acknowledged or ambiguous-timeout submissions;
- delayed `SUCCESS` and `FAILURE` resolution;
- stable idempotency-key duplicate responses;
- authoritative verification;
- compensation when explicitly supported; and
- restart by reopening its provider-owned SQLite database.

`python -m effectguard.p4.local_provider --database PATH --port PORT` runs the
provider as a standalone local HTTP service. Tests use its durable direct
interface because the restricted test sandbox cannot bind loopback sockets;
one standalone loopback submit/resolve check passed outside that restriction.

## Guarantees and Non-Guarantees

The adapter demonstrates locally durable evidence handling and an independent
authoritative-state boundary. It does not prove a remote provider accepted an
idempotency contract, provide distributed transactions, or guarantee exactly
once delivery. A future external integration must document provider-side
idempotency retention, verification semantics, compensation behavior, timeout
ambiguity, and billing/availability failure modes.
