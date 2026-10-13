# P4 Temporal Equivalence Challenge

## Question

Can a capability-complete Temporal application implement the behavior proposed
for EffectGuard? The answer is **yes, in principle**, subject to the same
provider and application assumptions. This is a design-equivalence assessment,
not a claim that the current local Temporal prototype has demonstrated every
behavior.

## What Temporal Natively Supplies

Temporal persists a complete Workflow Event History and replays it after a
worker failure to reconstruct workflow state. Activity results are recorded so
that replay does not repeat completed activity calls. See the official
[Event History documentation](https://docs.temporal.io/encyclopedia/event-history)
and [Workflow documentation](https://docs.temporal.io/workflows).

Temporal does not determine application-specific semantics for an external
operation. Activities interact with the external world; application code must
define logical IDs, idempotency, verification, compensation, and any policy
for an ambiguous outcome. This division is expected, not a limitation unique to
Temporal. Its operation documentation also explicitly discusses at-least-once
execution and the need for idempotency in relevant integrations.

## Capability-Complete Temporal Construction

| EffectGuard element | Faithful Temporal implementation | Equivalent behavior? |
| --- | --- | --- |
| Durable logical operation identity | Derive a stable operation ID from workflow ID plus a deterministic operation key; pass it as the provider idempotency key. Persist the mapping in Temporal history and provider state. | Yes, if the provider honors the key. |
| Effect receipt | An Activity returns a structured receipt containing observation time, provider operation ID, status, verification evidence, and capability metadata. The receipt is retained in Activity results/history or an application store. | Yes. |
| `VALID`/`INVALID`/`UNKNOWN` classification | A deterministic Workflow function invokes a versioned, application-defined classifier over durable receipt evidence and declared provider capabilities. | Yes. Temporal does not supply the predicate, but neither does it preclude it. |
| Verification of ambiguous commit | A verification Activity queries an authoritative provider using the stable operation ID. The result is recorded durably. | Yes, subject to provider query capability. |
| Conflict-cone barrier | The Workflow maintains an explicit dependency/conflict graph and schedules no irreversible conflicting Activity while any prerequisite remains `UNKNOWN`. | Yes. This is application policy. |
| Compensation | A compensating Activity uses stable logical IDs and verifies the compensating result. | Yes, subject to provider capability. |
| `UNRESOLVED` or `RECOVERY_UNSUPPORTED` | The Workflow returns a typed terminal result, or waits for a signal/operator decision, without claiming recovery. | Yes. |
| Independent final-state evaluation | A post-completion evaluator reads serialized workflow/provider traces and hidden benchmark truth outside the Temporal worker. | Yes; this is evaluation architecture rather than a Temporal feature. |

## Equivalence Limits

Equivalence requires an honest baseline, not merely a standard Temporal retry
configuration. The Temporal comparison must receive the same public provider
receipts, verification API, idempotency contract, declared reversibility,
compensation ability, dependency/conflict graph, deadlines, and terminal-status
definitions as EffectGuard.

Conversely, EffectGuard cannot produce safety when the provider offers neither
idempotency nor authoritative verification and an irreversible conflict exists.
A Temporal workflow facing the same evidence should reach the same block,
unresolved, or unsupported outcome. Such an outcome is evidence about provider
capabilities, not platform superiority.

## What Could Still Be Evaluated

The research question can compare policy designs only if their shared
application-level mechanisms are controlled. A valid comparison is:

1. Temporal durable replay plus stable IDs, verification, and idempotency.
2. The same Temporal application plus a RETRO-like semantic predicate or
   pause/escalation policy.
3. The same application plus EffectGuard's explicit `UNKNOWN` and conflict-cone
   policy.

The measured contrast is then the policy, not durable execution. If the
EffectGuard policy offers no safety/selectivity/availability improvement over
the strong Temporal policy, the runtime architecture does not support a
separate algorithmic contribution.

## Fairness Requirements

- Use the same provider implementation and external observations.
- Use the same stable logical operation IDs and idempotency behavior.
- Give both systems the same verification deadline and retry budget.
- Apply the same compensation capability and final invariants.
- Keep runtime policy separate from the sealed evaluator for every arm.
- Report blocking, unresolved, unsupported, failed, unsafe, and recovered
  outcomes, rather than scoring only successful completion.

## Decision

Temporal is not an adversarially weakened baseline. It can host the proposed
EffectGuard behavior as application code. Therefore the defensible research
claim is a policy/framework claim unless a paired evaluation demonstrates that
the specified policy yields a reproducible advantage over a capability-matched
Temporal implementation and a RETRO-like semantic baseline.
