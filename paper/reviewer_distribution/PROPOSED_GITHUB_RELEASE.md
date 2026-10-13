# Proposed GitHub Release

## Proposed tag

`p4-development-reproducibility-v0.1`

This is a proposal only. No Git tag, GitHub release, archive, DOI, or public
publication has been created.

## Proposed title

EffectGuard P4 Development Reproducibility Candidate v0.1

## Draft release notes

**DEVELOPMENT-ONLY.** This release candidate documents a locally reproduced,
service-backed EffectGuard--Temporal witness for a retryable pre-commit failure
followed by a lost acknowledgement after commit.

It includes the shared provider-owned fault script, receipt/audit provider,
common execution harness, Temporal Java integration, regression tests, and
reviewer reproduction materials.

The artifact verifies one paired witness only. It does not establish general
recovery safety, restart tolerance, performance, comparative superiority,
algorithmic novelty, independent benchmark validity, or independent review.
P3 mixed findings and P4 limitations remain preserved.

Start with `paper/release_candidate/README.md` and
`paper/release_candidate/CLEAN_CLONE_VERIFICATION_REPORT.md`.

## Release-owner checks before publication

- Push the exact reviewed branch and commits.
- Create and verify an annotated tag against the final reviewed SHA.
- Re-run secret, license, and artifact-size checks on the final remote state.
- Do not include local databases, virtual environments, process logs, sealed
  benchmark data, or unreviewed historical artifacts.
- Keep all wording labeled DEVELOPMENT-ONLY.
