# Security and License Audit

## Candidate contents

The candidate contains Markdown documentation and repository-relative links.
It does not embed source archives, databases, provider logs, API keys,
credentials, personally identifying information, or sealed benchmark outcomes.

## Scan scope and result

A content scan of `paper/release_candidate/` searched for common credential
markers and local absolute paths. No credential-like values or absolute
machine-specific paths should be included in the package. This is a release
preparation check, not a substitute for secret-scanning the final Git commit or
archive.

## Provenance and licenses

- EffectGuard source is governed by the repository's root license, which a
  release owner must verify before publication.
- Temporal Java SDK is declared as version 1.40.0 in
  `temporal-baseline/pom.xml`; its license must remain attributed according to
  upstream requirements.
- WfCommons materials, if later included, require the documented dataset
  provenance and license review. No WfCommons dataset is copied here.
- No Google, OpenAI, Gemini, or other paid-provider credentials or outputs are
  part of this candidate.

## Required release-owner checks

1. Commit the reviewed source snapshot and record a commit hash.
2. Run a repository secret scanner against the final archive.
3. Verify root and third-party licenses, notices, and attribution.
4. Remove local databases, `target/`, virtual environments, logs, and all
   unreviewed generated results from the archive.
5. Obtain an independent reproduction before public release.
