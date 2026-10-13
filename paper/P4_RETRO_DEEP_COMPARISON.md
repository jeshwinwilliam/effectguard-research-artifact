# P4 RETRO Deep Comparison

## Source and Scope

This review reads Kim, Wang, Zeldovich, and Kaashoek's full OSDI 2010 paper,
*Intrusion Recovery Using Selective Re-execution* (RETRO), not only its
abstract. The source is available from the [USENIX paper page](https://www.usenix.org/legacy/event/osdi10/tech/full_papers/Kim.pdf).
The comparison identifies what RETRO directly demonstrates, what it does not
discuss, and what therefore cannot be claimed as unique to EffectGuard.

## Capability-by-Capability Assessment

| Capability | RETRO evidence | Assessment for EffectGuard |
| --- | --- | --- |
| Semantic predicates | Each action exposes `equiv()` to determine whether inputs are semantically changed. If inputs remain equivalent, RETRO skips re-execution. | Directly supported. EffectGuard must not claim semantic validity checking or preservation of semantically unaffected downstream work as new. |
| Dependency tracking | RETRO records an action history graph with ordered action, actor, and data-object dependencies. It refines graph objects to reduce false dependencies. | Directly supported. A dependency graph, refinement, or downstream affected-set calculation is not new. |
| Selective re-execution | The controller rolls back affected objects, then re-executes only actions whose input semantics changed or whose outputs need reconstruction. | Directly supported. This is the closest prior mechanism to EffectGuard's selective recovery. |
| Compensation or repair | RETRO uses compensating actions for external dependencies where possible. For some network dependencies, it may ignore, resend, or require a user to resolve the dependency. | Directly supported. EffectGuard must not claim external-effect compensation or an explicit unresolved path as new in isolation. |
| Recovery correctness conditions | The design aims to reconstruct a state in which the attack did not occur while preserving legitimate actions. It relies on complete-enough logs, checkpoints, trusted kernel/filesystem/log state, and action-manager semantics. | Supported as a system-specific goal and assumption set. It is not a general formal proof for arbitrary third-party tool APIs. |
| External-effect assumptions | RETRO recognizes externally visible dependencies. It assumes applicable compensations when available; otherwise it pauses and asks an administrator to decide or re-execute. | Directly supported. Its external effects are operating-system/network interactions rather than provider receipts with explicit capabilities. |
| Ambiguous operation outcomes | The paper does not define a three-valued receipt outcome, provider-query protocol, timeout/commit ambiguity model, or automatic conflict-cone policy. Unresolvable external dependencies are escalated to the administrator. | Not established as an explicit runtime model. This is the narrowest remaining distinction, but it requires direct evidence that the proposed policy adds value beyond a RETRO-style pause/escalation rule. |

## Important RETRO Mechanics

RETRO replaces an identified offending action with a benign action, rolls back
affected objects to checkpoints, and advances through a repaired timeline. Its
repair manager API includes rollback, redo, dependency connection, and semantic
equivalence. During repair, equivalent actions are skipped; non-equivalent
ones are re-executed. The full paper states that action managers record enough
information for both re-execution and semantic-equivalence checking.

The paper also makes conservative recovery decisions. It records system-wide
dependencies, preserves coarse dependencies when finer-grained managers are
not trusted, and requests administrator input for conflicts or external
dependencies that it cannot safely resolve. These are important precedents for
the proposed EffectGuard barrier behavior.

## Material Differences That Are Real but Not Yet Contributions

| Dimension | RETRO | EffectGuard proposal | Why this is not automatically novelty |
| --- | --- | --- | --- |
| Trigger | Known offending/attack actions chosen by an administrator | Timeout, delayed visibility, duplicate delivery, or missing provider evidence | A different failure model can motivate adaptation, but does not by itself establish a new algorithm. |
| Evidence | System logs, checkpoints, and manager-specific predicates | Logical operation IDs, provider receipts, verification calls, and declared capabilities | A provider-facing contract is a potentially useful interface contribution, subject to comparison against an application that implements the same contract. |
| Unresolved state | Pause and request a human decision when external replay/compensation is unavailable | `UNKNOWN`, conflict-cone block, `UNRESOLVED`, or `RECOVERY_UNSUPPORTED` | Explicit terminal states may improve auditability, but must be shown to improve safety/availability tradeoffs. |
| Evaluation boundary | System repair and scenario-specific correctness | Runtime selection separated from post-execution final-invariant evaluation | Evaluator separation is valuable experimental methodology, not evidence of a new runtime algorithm by itself. |

## Consequences for the Paper

1. Remove any claim of first semantic selective recovery, first effect-aware
   recovery, or first selective downstream preservation.
2. Do not use the word “semantic” as the primary differentiator from RETRO.
3. Frame the strongest remaining claim as a testable agent-workflow policy:
   a receipt and capability contract plus a conservative `UNKNOWN` decision
   rule under ambiguous provider outcomes.
4. Include a RETRO-like semantic-recovery baseline, or explicitly limit the
   paper to a design/framework contribution. A dependency-only baseline is not
   sufficient to establish differentiation from RETRO.
5. Require a negative control where a RETRO-style pause/escalation policy is
   equally safe or more available. Otherwise, EffectGuard's additional policy
   is not empirically justified.

## Bottom Line

RETRO already covers the central mechanism previously described as
EffectGuard's novelty: semantically selective downstream recovery with
dependency tracking and compensation. The only plausible technical distinction
is not “semantic recovery,” but the treatment of *provider-visible ambiguous
outcomes* using explicit receipt capabilities and conservative terminal states.
That distinction remains a hypothesis, not an established contribution.
