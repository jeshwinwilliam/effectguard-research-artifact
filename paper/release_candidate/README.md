# EffectGuard P4 Reviewer Reproducibility Release Candidate

This directory is a development-only reviewer handoff. It documents a single
real-service paired witness: a retryable pre-commit provider failure followed
by a committed effect whose acknowledgement is withheld. EffectGuard and a
Temporal Java workflow consumed separate, freshly initialized providers loaded
with the same fault script.

This is **not** a public release, a confirmatory study, or evidence of general
comparative superiority. The release candidate is intentionally marked partial:
the source and script required to reproduce the witness are currently
uncommitted at the repository's evidence-freeze commit.

Read in this order:

1. [Artifact manifest](ARTIFACT_MANIFEST.md)
2. [Reproducibility guide](REPRODUCIBILITY_GUIDE.md)
3. [Expected results](EXPECTED_RESULTS.md)
4. [Known limitations](KNOWN_LIMITATIONS.md)
5. [Security and license audit](SECURITY_AND_LICENSE_AUDIT.md)
6. [Release readiness report](RELEASE_READINESS_REPORT.md)

This curated snapshot has an isolated history. See
`paper/reviewer_distribution/CLEAN_BRANCH_AUDIT.md` and
`paper/reviewer_distribution/CLEAN_BRANCH_REPRODUCIBILITY.md` before publication
or distribution.
