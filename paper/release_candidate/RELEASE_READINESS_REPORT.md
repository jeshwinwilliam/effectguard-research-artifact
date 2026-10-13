# Release Readiness Report

## Integrity preflight

- Branch: `p4-unknown-safe-recovery`.
- Reviewed runtime-source commit: `b72be6e7fa7cdb9620a25d61323e2bc61085f0dd`.
- Evidence boundary: `paper/P4_DEVELOPMENT_EVIDENCE_FREEZE.md`.
- Claim boundary: `paper/P4_SUPPORTED_CLAIMS_MATRIX.md`.
- External review handoff: `paper/external_review/`.
- Historical P3 and P4 result directories were not modified by this release
  preparation.

## Independent-use simulation

A fresh detached worktree at the reviewed runtime-source commit was clean
before setup. It installed using the documented development dependency set and
reproduced the two-arm witness with new Temporal and provider SQLite state.
Both arms met the stated terminal, retry, submission, verification, descendant,
graph-identity, logical-operation-identity, and evaluator-validity checks.
Provider audit hashes and exact test results are recorded in
`CLEAN_CLONE_VERIFICATION_REPORT.md`.

## Release decision

The candidate is ready for controlled reviewer sharing. The verified result is
still one development-only witness, so publication or scientific claims remain
bounded by `KNOWN_LIMITATIONS.md` and require independent review.

## Proposed release notes, not published

> EffectGuard P4 development reproducibility candidate documents one
> service-backed paired retry/lost-acknowledgement witness. It includes
> provider-audit evidence and a limited common-metric contract. It does not
> report confirmatory results, general Temporal superiority, independent
> benchmark validation, or algorithmic novelty.

## Archival-readiness checklist

- [x] Commit and hash the reviewed source snapshot.
- [x] Reproduce the witness from a fresh detached checkout with fresh services.
- [ ] Reproduce on an independent second machine or reviewer environment.
- [ ] Archive only development-safe data and all necessary scripts.
- [ ] Complete secret, personal-data, and license review of the final archive.
- [ ] Obtain required independent correctness, benchmark, statistical, and
  baseline-fidelity feedback.
- [ ] Keep confirmatory protocol and sealed benchmarks outside the release
  until authorized.

RELEASE CANDIDATE READY — PUBLICATION AUTHORIZATION REQUIRED
