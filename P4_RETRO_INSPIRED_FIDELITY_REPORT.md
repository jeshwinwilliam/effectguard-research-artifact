# P4 RETRO-Inspired Baseline Fidelity Report

## Identity and Scope

`effectguard.p4.retro_inspired.RetroInspiredSemanticRecovery` is a
development-only policy inspired by selected documented RETRO concepts. It is
not the original RETRO system, a reproduction, or a substitute for an original
RETRO deployment.

## Supported Development Capabilities

The policy consumes only the development harness's public request:

- declared action dependencies and conflicts;
- public provider receipts and observable statuses;
- a deterministic semantic-equivalence predicate;
- declared compensation and verification capabilities; and
- a pre-specified UNKNOWN pause/escalation policy.

It preserves actions with equivalent public inputs, marks descendants invalid
when required effects fail or conflicts are present, compensates/re-executes
eligible invalid actions, and returns `BLOCKED`, `UNRESOLVED`, or
`RECOVERY_UNSUPPORTED` when evidence or capability is inadequate.

## Material Differences From RETRO

| Area | This development baseline | Original-system fidelity claim |
| --- | --- | --- |
| Action history | Explicit in-memory workflow descriptors | Not a system-wide process/action history |
| Dependencies | Declared workflow edges and receipt requirements | Not automatic system-level provenance capture |
| Predicate | Small deterministic receipt-status equivalence rule | Not a validated general equivalence mechanism |
| Re-execution | Recovery plan steps in the test harness | Not process checkpoint/replay machinery |
| External effects | P4 provider receipts and declared compensation | Not RETRO's original external-effect model |
| UNKNOWN | Explicit conservative policy | An EffectGuard-study design choice, not attributed to RETRO |

## Fidelity Decision

The baseline is sufficient as a transparent development comparator for
semantic-policy behavior. It is not sufficient to support claims about RETRO's
measured behavior, performance, or correctness. Any confirmatory use requires
independent review of the predicate, graph contract, and source-paper mapping,
and must retain the `RETRO-inspired` label in all materials.
