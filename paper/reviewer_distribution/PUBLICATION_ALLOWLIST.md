# Publication Allowlist

## Purpose

This branch is a curated reviewer artifact, created from source commit
`1eafe684f1e2adbaea0fba9faf7631da5aeb51a2`. It is an orphan branch with no
parent history. The allowlist is intentionally narrow so reviewers receive the
P4 development witness without the historical P3 experiment archive.

## Included

- P4 Python runtime source: `effectguard/p4/`, `effectguard/models.py`, and the
  package initializer.
- Focused P4 tests: `tests/test_p4_common_execution.py`,
  `tests/test_p4_local_provider.py`, and `tests/test_p4_unknown_safe_recovery.py`.
- Temporal Java workflow, activity, and test source under `temporal-baseline/src/`
  with `temporal-baseline/pom.xml`.
- Versioned P4 development inputs:
  `experiments/p4/development_benchmark_v1.json` and
  `experiments/p4/shared_fault_script_v1.json`.
- Dependency declarations, license, P4 safety/fairness documentation, manuscript
  draft, release-candidate material, and external-review material.
- Compact development verification summary:
  `results/p4/release-candidate-clean-clone-v1/clean_clone_verification.json`.

## Excluded

- Excluded: all `results/p3/` campaign records, manifests, traces, tables, figures, and
  processed outputs.
- Raw P4 provider databases, service logs, uncommitted evidence directories, and
  sealed benchmark truth.
- WfCommons workflow instances and EffectGuard-specific annotation overlays.
- Generated Java `target/` directories, Python caches, virtual environments, and
  SQLite databases.
- Credentials, `.env` files, personal machine paths, and unreviewed binary files.

The included effect-annotation and WfCommons adapter source is implementation
code only; no external workflow dataset is included.
