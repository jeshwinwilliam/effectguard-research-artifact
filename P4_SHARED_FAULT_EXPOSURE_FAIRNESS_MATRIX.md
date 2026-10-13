# P4 Shared Fault Exposure Fairness Matrix

| Required case | Provider script | Both runtime arms integrated | Audit complete | Classification |
| --- | --- | --- | --- | --- |
| Retryable failure then success | Pre-commit failure implemented | Yes, fresh isolated witness | Complete provider audits | FAIR_AND_VERIFIED |
| Timeout after possible commit | Lost acknowledgement implemented | Yes, same fresh witness | Complete provider audits | FAIR_AND_VERIFIED |
| Delayed success/failure | Existing provider resolution | Existing common matrix only | Partial legacy evidence | FAIR_WITH_DOCUMENTED_LIMITATIONS |
| Persistent UNKNOWN | Existing provider state | Existing common matrix only | Partial legacy evidence | FAIR_WITH_DOCUMENTED_LIMITATIONS |
| Duplicate-safe retry | Existing idempotency | Existing common matrix only | Partial legacy evidence | FAIR_WITH_DOCUMENTED_LIMITATIONS |
| Provider interruption/restart | Missing | No | No | NOT_VERIFIED |
| Worker interruption/restart | Missing shared-provider path | No | No | NOT_VERIFIED |
| Compensation failure | Existing policy flag | Existing common matrix only | No provider fault audit | NOT_VERIFIED |
| Irreversible-effect protection | Existing semantic graph | Existing common matrix only | Partial legacy evidence | FAIR_WITH_DOCUMENTED_LIMITATIONS |

No row is `FAIR_AND_VERIFIED` until the same script is delivered to both arms
and each arm persists a provider-audit reference, physical attempts, final
provider state, and independent evaluator verdict.
