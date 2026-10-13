# Artifact Manifest

## Scope

The target witness is the development-only, two-arm scripted retry and
lost-acknowledgement case. It is not a representative benchmark or a
confirmatory experiment.

| Artifact | Repository-relative path | SHA-256 | Role |
| --- | --- | --- | --- |
| Evidence freeze | `paper/P4_DEVELOPMENT_EVIDENCE_FREEZE.md` | Documentation, no fixed hash in this candidate | Claim boundary and witness summary |
| Supported claims | `paper/P4_SUPPORTED_CLAIMS_MATRIX.md` | Documentation, no fixed hash in this candidate | Permitted and prohibited claims |
| Fault script | `experiments/p4/shared_fault_script_v1.json` | `4b36a2cbe3852d295a27b173bc9241a7fe3e8d58fea65117c45e520f2094e079` | Versioned provider-owned fault contract |
| EffectGuard common harness | `effectguard/p4/common_execution.py` | `facb68bd8eaf2771cd3eddc85c64eaf91092ae5d91a39a7a763159efcab67f2a` | Real P4 runtime arm |
| Local provider | `effectguard/p4/local_provider.py` | `4730504b1573506450a34835609f2cbe7aa64404399ee0f5eea7b031387539f5` | Provider receipts and audit ledger |
| Temporal recovery workflow | `temporal-baseline/src/main/java/org/effectguard/temporal/TemporalRecoveryWorkflowImpl.java` | `39ed76cd19d64062d82824f79fe00944ca671e253aafa762f87c8208e0f88cf7` | Real Temporal Java arm |
| Compact clean-checkout summary | `results/p4/release-candidate-clean-clone-v1/clean_clone_verification.json` | `7e698ea57cb1cd0a12cff56f46b42d50d87acdc65c09e1ec35220f9c6398e6ae` | Development-only verification summary |

## Source boundary

The curated source snapshot derives from reviewer-distribution commit
`1eafe684f1e2adbaea0fba9faf7631da5aeb51a2`; its verified release evidence is
commit `53fcf5e2796d4c92915ca45cf7155f980765ae4e`. It contains no raw historical
reconciliation trace. A reviewer can generate fresh audit evidence by following
the reproducibility guide.

All paths are intentionally repository-relative. This candidate packages no
credentials, provider databases, local process logs, or sealed benchmark data.
The compact verification summary is development-only and is retained at
`results/p4/release-candidate-clean-clone-v1/clean_clone_verification.json`.
