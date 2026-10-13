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

The audit checks confirm that those historical objects are absent from the
isolated repository itself; this is stronger than merely not listing them in a
branch log.

## Security and content checks

Before publication, the branch is checked for credentials, P3 record paths,
generated Java outputs, SQLite databases, large or binary artifacts, and
machine-specific absolute paths. The exact verification commands and results are
recorded in `CLEAN_BRANCH_REPRODUCIBILITY.md`.

The selected source hashes are:

- `effectguard/p4/common_execution.py`:
  `facb68bd8eaf2771cd3eddc85c64eaf91092ae5d91a39a7a763159efcab67f2a`
- `effectguard/p4/local_provider.py`:
  `4730504b1573506450a34835609f2cbe7aa64404399ee0f5eea7b031387539f5`
- `TemporalRecoveryWorkflowImpl.java`:
  `39ed76cd19d64062d82824f79fe00944ca671e253aafa762f87c8208e0f88cf7`
- `experiments/p4/shared_fault_script_v1.json`:
  `4b36a2cbe3852d295a27b173bc9241a7fe3e8d58fea65117c45e520f2094e079`

## Scientific boundary

The artifact supports reproduction of one development-only real-service paired
retry/lost-acknowledgement witness. It does not establish comparative superiority,
algorithmic novelty, independent validation, or a confirmatory result.
