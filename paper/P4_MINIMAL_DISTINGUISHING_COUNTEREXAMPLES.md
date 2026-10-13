# P4 Minimal Distinguishing Counterexamples

## Purpose

These are minimal thought experiments for a sealed evaluation design. They do
not establish that EffectGuard wins. Each comparison grants a competing system
all capabilities explicitly stated in its row; a result is meaningful only if
the baseline does not receive less public evidence or fewer provider features.

## Shared Notation

`submit(id, request)` is an externally visible operation with stable logical ID
`id`. `verify(id)` returns authoritative provider evidence only if the provider
supports verification. A final invariant can inspect the provider's authoritative
state after the run, but that hidden truth is unavailable to runtime policy.

| Example | Preconditions | Ordinary retry/replay | Semantic selective recovery | UNKNOWN-aware conservative policy | Can a strong competitor do the same? |
| --- | --- | --- | --- | --- | --- |
| E1: Duplicate-safe timeout | `submit(k, A)` times out after commit; provider accepts `k` idempotently and `verify(k)` later returns committed. | A retry with `k` is safe; replay can continue after confirmation. | Can preserve dependent work if its input is unchanged. | Classify temporarily `UNKNOWN`, verify, then `VALID`; no conflict barrier is needed. | Yes. This distinguishes neither EffectGuard nor semantic recovery; idempotency and verification suffice. |
| E2: Semantic preservation after invalid input | A cached price used by `plan()` is later found invalid; unrelated `notify()` reads no affected state. | Broad replay may repeat both actions. | Re-executes `plan()` while preserving `notify()` if the predicate confirms its inputs are equivalent. | Makes the same preservation decision when evidence is complete. | Yes. RETRO directly supports this pattern. This is not an EffectGuard differentiator. |
| E3: Irreversible fallback conflict | `submit(k, A)` times out; provider gives no verification until later. A fallback `submit(k2, B)` would violate the invariant if A committed. Neither operation is compensable. | A naive retry/replay or fallback can duplicate/conflict. A safe implementation must avoid the fallback. | A semantic predicate can conservatively treat the dependency as unresolved and pause. | Marks A `UNKNOWN`, blocks the conflict cone, and returns `UNRESOLVED` at deadline. | Yes. A Temporal workflow or RETRO-like controller can encode the same no-fallback rule. The difference is explicit typed policy/auditability, not expressiveness. |
| E4: UNKNOWN outside the conflict cone | `submit(k, A)` is unresolved, but a read-only `prepare(C)` shares no state and cannot violate an invariant. | Broad blocking may halt all work. | May preserve `prepare(C)` if the dependency graph proves independence. | Preserves C but blocks only irreversible conflicting actions. | Yes, if the competitor has the same graph and conflict predicate. This tests policy precision, not a unique mechanism. |
| E5: Verification contradicts optimistic plan | An agent plans shipment based on `UNKNOWN` reservation A, then `verify(k)` proves A failed. Shipment depends semantically on A; notification does not. | Replay may duplicate or retain stale shipment. | Re-executes shipment; can preserve notification if predicate says it remains valid. | Sets A and shipment `INVALID`, preserves notification only after certificate, and records the reason. | Yes. RETRO-like predicates and a strong Temporal application can implement the same decision; EffectGuard must show fewer policy mistakes or clearer audit guarantees. |
| E6: No verification and failed compensation | A possibly committed irreversible charge cannot be verified or compensated. A downstream booking conflicts with a committed charge. | Retrying is unsafe; replay cannot make evidence appear. | A sound implementation must stop/escalate. | Returns `RECOVERY_UNSUPPORTED` or `UNRESOLVED`; never reports `RECOVERED`. | Yes. This is a necessary negative control: a correct strong baseline should tie EffectGuard. |

## Distinctions That Survive the Examples

1. **Ordinary retry/replay** is inadequate only when it lacks stable IDs,
   provider verification, and a domain policy for ambiguous effects. It is not
   an adequate strong baseline.
2. **Semantic selective recovery** already covers preservation of unaffected
   downstream work in E2 and E5.
3. **UNKNOWN-aware conservative recovery** specifies a useful terminal policy
   for E3 and E6, but it is implementable in other programmable orchestrators.
4. **EffectGuard's potential contribution** is a reusable, auditable contract
   and evaluation method for applying that policy to agent-tool workflows. It
   is not established as a more expressive recovery algorithm.

## Required Negative Controls

- E1 must show no artificial advantage: all capability-matched strategies
  should safely recover.
- E2 must allow a RETRO-like semantic baseline to match EffectGuard's recovery
  work.
- E6 must allow safe baselines to block or return unsupported rather than
  penalizing them for refusing an unsafe recovery.
- At least one independently authored template must make a strong baseline
  match or outperform EffectGuard. Otherwise the benchmark may encode the
  proposed policy's answer rather than test it.
