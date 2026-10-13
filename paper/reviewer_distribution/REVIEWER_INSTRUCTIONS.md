# Reviewer Instructions

## Scope

This artifact is development-only. It documents one verified, real-service
EffectGuard--Temporal retry/lost-acknowledgement witness. It is not a
confirmatory experiment, a sealed benchmark, or a claim of superiority.

## Obtain the verified revision

After the release owner makes the reviewer branch accessible, run:

```bash
git clone https://github.com/jeshwinwilliam/EffectGuard.git
cd EffectGuard
git checkout 53fcf5e2796d4c92915ca45cf7155f980765ae4e
git status --short
```

The expected status is empty. Verify release scope before running anything:

```bash
git show --no-patch --format='%H%n%s' HEAD
shasum -a 256 \
  effectguard/p4/common_execution.py \
  effectguard/p4/local_provider.py \
  temporal-baseline/src/main/java/org/effectguard/temporal/TemporalRecoveryWorkflowImpl.java \
  experiments/p4/shared_fault_script_v1.json
```

## Read first

1. `paper/release_candidate/README.md`
2. `paper/release_candidate/CLEAN_CLONE_VERIFICATION_REPORT.md`
3. `paper/release_candidate/KNOWN_LIMITATIONS.md`
4. `paper/P4_SUPPORTED_CLAIMS_MATRIX.md`

## Reproduce the development witness

Follow `paper/release_candidate/REPRODUCIBILITY_GUIDE.md` exactly. It creates
only fresh local Temporal and SQLite provider state. The expected witness
metrics are in `paper/release_candidate/EXPECTED_RESULTS.md`; the recorded
machine-readable evidence is
`results/p4/release-candidate-clean-clone-v1/clean_clone_verification.json`.

Do not run a confirmatory benchmark, alter fault schedules, use paid models, or
interpret a matching terminal state as general recovery equivalence.
