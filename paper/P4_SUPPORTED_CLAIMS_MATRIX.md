# P4 Supported Claims Matrix

| Candidate claim | Status | Evidence | Boundary |
| --- | --- | --- | --- |
| UNKNOWN outcomes can be represented conservatively in the P4 development runtime. | Supported, development-only | P4 safety specification and UNKNOWN development controls. | Not independently reviewed or benchmark validated. |
| Stable logical IDs and provider idempotency can prevent duplicate commitment in the local provider. | Supported, development-only | Local-provider tests and duplicate controls. | Applies to this local provider contract only. |
| EffectGuard and a real Temporal Java workflow can consume the same scripted pre-commit failure and lost acknowledgement. | Supported for one witness | `two-arm-fault-exposure-v1` reconciliation and provider audits. | One travel development graph; not a general Temporal comparison. |
| Both arms can recover the witnessed scripted case without an invalid evaluator verdict. | Supported for one witness | Real-service witness and matching provider metrics. | Does not imply general recovery correctness. |
| Common logical recovery-action and physical-provider counters can be reported separately. | Supported, development-only | `P4_COMMON_METRIC_CONTRACT.md` and metric-evidence repair. | Broader fault families lack complete audits. |
| EffectGuard is safer, more available, or more efficient than Temporal. | Unsupported | No representative paired fault matrix or independent benchmark. | Must not be claimed. |
| EffectGuard has general restart tolerance comparable to Temporal. | Unsupported | Restart paths are not paired through the shared provider. | Must not be claimed. |
| EffectGuard is a new selective-recovery algorithm beyond RETRO or application-level Temporal logic. | Unsupported | Novelty challenge narrowed the contribution. | Treat as an evaluation/policy framework question. |

## Claim-Scope Rules

The manuscript may describe the implementation, local provider contract, and
the narrow scripted witness. It must call all P4 observations development-only,
identify author-created overlays, retain negative P3 evidence, and state that
Temporal can implement application-defined semantic validity and UNKNOWN
policies. It must not pool P3 attempts, report a general baseline win, or
equate matching terminal status with equivalent fault behavior.
