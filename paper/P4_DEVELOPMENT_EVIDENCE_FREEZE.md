# P4 Development Evidence Freeze

## Freeze Boundary

This document freezes the interpretation of current P4 development-only
evidence. It is not a preregistration freeze and does not authorize a
confirmatory experiment. The active branch is `p4-unknown-safe-recovery` at
Git commit `0ba29b2a804adc39ba859b6dbeec8ac88ba69853`; the engineering work is
uncommitted. Historical P3 directories remain untracked and unchanged.

## Source and Evidence Identifiers

| Item | SHA-256 |
| --- | --- |
| `effectguard/p4/common_execution.py` | `facb68bd8eaf2771cd3eddc85c64eaf91092ae5d91a39a7a763159efcab67f2a` |
| `effectguard/p4/local_provider.py` | `4730504b1573506450a34835609f2cbe7aa64404399ee0f5eea7b031387539f5` |
| Temporal recovery workflow | `39ed76cd19d64062d82824f79fe00944ca671e253aafa762f87c8208e0f88cf7` |
| Shared fault script | `4b36a2cbe3852d295a27b173bc9241a7fe3e8d58fea65117c45e520f2094e079` |
| Two-arm reconciliation | `0dc481de68b5587d23ef2095dcea778df5e4f0e84e64ecb72d2b88e9c1d217b0` |

## Completed Development Evidence

- P4 deterministic development pilots: `results/p4/development-pilot-v1/` and
  `results/p4/development-pilot-v2-fair-baselines/`.
- Service-backed Temporal feasibility: `results/p4/sprint3e-service-backed-temporal-v1/`.
- Common-metric reconciliation: `results/p4/common-metrics-evidence-repair-v1/`.
- Root-compensation parity: `results/p4/root-compensation-parity-v1/`.
- Two-arm provider-script witness: `results/p4/two-arm-fault-exposure-v1/`.

The final witness used separate fresh local providers loaded with the same
versioned script. Both arms produced a provider audit with a retryable failure
before commitment, a committed effect with withheld acknowledgement, receipt
resolution, and verification. Both reached `RECOVERED` with one retry, two
provider submissions, two verifications, and one actual descendant effect.
This is one development witness, not a representative benchmark result.

## Fault-Family Status

| Fault family | Status | Basis |
| --- | --- | --- |
| Retryable pre-commit failure followed by success | VERIFIED | Real Temporal service, real EffectGuard runtime, separate scripted providers, authoritative audits. |
| Lost acknowledgement after commit | VERIFIED | Same witness; provider recorded commit before acknowledgement withholding. |
| Delayed success/failure | PARTIALLY_VERIFIED | Common development matrix and provider resolution behavior; no shared scripted audit witness. |
| Persistent UNKNOWN | PARTIALLY_VERIFIED | Development matrix showed conservative terminal handling; no shared deadline-clock audit. |
| Duplicate-safe submission | PARTIALLY_VERIFIED | Provider idempotency and development controls exist; no shared scripted retry audit. |
| Compensation failure | PARTIALLY_VERIFIED | Deterministic development policy cases exist; no paired provider-fault audit. |
| Irreversible-effect protection | PARTIALLY_VERIFIED | Semantic graph development controls exist; no sealed independent benchmark. |
| Provider interruption/restart | NOT_VERIFIED | No provider-restart script or paired evidence. |
| Worker interruption/restart | NOT_VERIFIED | No paired shared-provider restart harness. |
| Deadline/retry exhaustion | NOT_VERIFIED | No common deadline clock or retry-exhaustion script. |

## Freeze Interpretation

The evidence supports a narrow engineering statement: the current adapters can
execute one provider-audited ambiguous-effect scenario with a real Temporal
service and retain externally visible retry and receipt evidence. It does not
establish broad recovery safety, fault tolerance, restart behavior, performance,
or comparative superiority.
