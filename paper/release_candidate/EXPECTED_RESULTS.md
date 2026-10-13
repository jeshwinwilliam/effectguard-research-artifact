# Expected Results

For the one supported development witness, each arm should retain auditable
evidence of the same external fault exposure, while preserving its native
runtime behavior.

| Observation | Expected EffectGuard | Expected Temporal |
| --- | --- | --- |
| Provider script version | `p4-shared-fault-script-v1` | `p4-shared-fault-script-v1` |
| First submit | Retryable failure before commit | Retryable failure before commit |
| Next submit | Commit followed by withheld acknowledgement | Commit followed by withheld acknowledgement |
| Receipt path | Resolution and verification recorded | Resolution and verification recorded |
| Terminal classification | `RECOVERED` | `RECOVERED` |
| Retry attempts | 1 | 1 |
| Provider submissions | 2 | 2 |
| Provider verifications | 2 | 2 |
| Actual descendant effects | 1 | 1 |

The provider audit, not terminal status alone, is the authoritative evidence
for physical attempts and receipt transitions. Temporal may additionally report
native scheduling or replay events. Do not require equal internal scheduler
traces or infer safety beyond this witness.

The original raw reconciliation is excluded from this history-isolated snapshot.
Compare fresh output with the explicit contract in this file and record any
differences, including baseline wins, failures, or unresolved outcomes rather
than normalizing them away.

The same metrics were observed in the final clean-clone verification. Its
compact, machine-readable evidence is
`results/p4/release-candidate-clean-clone-v1/clean_clone_verification.json`.
