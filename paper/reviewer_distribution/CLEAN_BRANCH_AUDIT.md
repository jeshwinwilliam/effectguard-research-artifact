# Clean Reviewer Branch Audit

## Provenance

- Original verified release commit:
  `53fcf5e2796d4c92915ca45cf7155f980765ae4e`.
- Original reviewer-distribution commit:
  `1eafe684f1e2adbaea0fba9faf7631da5aeb51a2`.
- Curated branch: `p4-reviewer-artifact-v0.1`.
- Construction method: an explicit `git archive` allowlist from the
  reviewer-distribution commit into a new orphan repository; no historical commit
  was cherry-picked.

## History boundary

The initial commit of this branch has no parent. It therefore cannot reach the
historical P3 artifact commits `4fefb4c` or `d0d08ac`. This is a curated snapshot,
not a preservation of the development branch's history.

## Security and content checks

Before publication, the branch is checked for credentials, P3 record paths,
generated Java outputs, SQLite databases, large or binary artifacts, and
machine-specific absolute paths. The exact verification commands and results are
recorded in `CLEAN_BRANCH_REPRODUCIBILITY.md`.

## Scientific boundary

The artifact supports reproduction of one development-only real-service paired
retry/lost-acknowledgement witness. It does not establish comparative superiority,
algorithmic novelty, independent validation, or a confirmatory result.
