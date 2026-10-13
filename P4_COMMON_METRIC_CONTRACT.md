# P4 Common Metric Contract v1

`p4-common-metrics-v1` reports additive, unweighted counters. It does not
define a composite score and does not replace legacy `recovery_work` fields.

| Counter | Rule |
| --- | --- |
| `logical_recovery_actions` | Compensation, re-execution, and recomputation plan units only. |
| `provider_submissions` | Actual HTTP provider submit requests, including valid descendants. |
| `provider_verifications` | Actual provider verify requests. |
| `compensation_attempts` | Actual provider compensation requests. |
| `retry_attempts` | Attempts beyond the first provider Activity attempt. |
| `duplicate_submissions` | Provider submissions acknowledged as duplicates. |
| `semantic_validity_evaluations` | Per-action public graph predicate decisions. |
| `blocked_or_skipped_descendants` | Descendants not submitted because their decision was INVALID or UNKNOWN. |
| `actual_descendant_effects` | Valid descendants submitted and resolved through the provider. |
| `scheduler_or_replay_events` | Platform-specific execution events, never combined with recovery work. |

Historical `7` and `4` remain intact. They are NOT_DERIVABLE as v1 common
metrics because neither original witness persisted the complete event ledger.
