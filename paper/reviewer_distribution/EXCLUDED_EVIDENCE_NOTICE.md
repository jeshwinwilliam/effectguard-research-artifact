# Excluded Evidence Notice

## Snapshot Boundary

This reviewer artifact includes the source, versioned fault script, focused
tests, reproducibility instructions, expected outcome contract, and compact
clean-checkout verification summary needed to reproduce one development-only
service-backed witness.

Historical P3 campaigns and historical P4 raw provider-audit reconciliations,
pilot directories, restart/deadline experiments, runtime databases, and service
logs are intentionally excluded. They remain outside this history-isolated
snapshot and are **not independently reproducible from this artifact**.

## What Reviewers Can Verify Here

- The included retry/lost-acknowledgement witness can be rerun with fresh local
  Temporal and provider services using the release-candidate reproducibility
  guide.
- The resulting fresh provider audits, receipts, and evaluator verdicts can be
  inspected locally.
- The compact clean-checkout summary records the prior development-only result;
  it is not a substitute for the excluded raw audit trace.

## What Remains Unverified Here

- Historical P3 outcomes and campaign-level claims.
- Other P4 pilot observations.
- Restart, interruption, and deadline fault families beyond the documented
  witness.
- Independent correctness, benchmark, statistical, or baseline-fidelity review.

No excluded material is silently represented as included evidence. Reviewers
should treat unavailable historical evidence as unavailable rather than infer it
from terminal statuses or summaries.
