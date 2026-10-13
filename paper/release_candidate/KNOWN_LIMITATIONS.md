# Known Limitations

- Only one real-service paired fault witness is fully verified: retryable
  pre-commit failure plus lost acknowledgement after commit.
- Delayed outcomes, persistent UNKNOWN, duplicate-safe submission,
  compensation failure, and irreversible-effect behavior are development-only
  partial evidence, not paired provider-script witnesses.
- Provider restart, worker restart, deadline behavior, and retry exhaustion
  are not verified in a common two-arm protocol.
- EffectGuard is not established as safer, more available, or more efficient
  than Temporal. Temporal can implement application-defined semantic validity
  and UNKNOWN policies.
- The RETRO comparison limits any claim that this is a new semantic
  selective-recovery algorithm.
- WfCommons topology is externally sourced, but EffectGuard external-effect
  annotations are synthetic until independently curated.
- P3-C9 contains mixed evidence, including negative S9 UNKNOWN results. It is
  preserved as historical evidence and is not pooled with P4 development data.
- No independent correctness, statistical, benchmark, Temporal-fidelity, or
  RETRO-fidelity review has occurred.
- No confirmatory P4 experiment has been authorized.

See `paper/P4_DEVELOPMENT_EVIDENCE_FREEZE.md`,
`paper/P4_SUPPORTED_CLAIMS_MATRIX.md`, and
`paper/external_review/P4_EXTERNAL_VALIDATION_DECISION_GATE.md` for the full
scope and review requirements.
