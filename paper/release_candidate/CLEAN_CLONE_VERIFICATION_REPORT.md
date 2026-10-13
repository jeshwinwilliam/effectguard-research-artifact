# Clean-Clone Verification Report

## Scope

This report records one fresh, development-only reproduction of the paired
retry/lost-acknowledgement witness. It is not a confirmatory evaluation and
does not change the development-evidence claim boundary.

## Source and environment

- Runtime-source commit: `b72be6e7fa7cdb9620a25d61323e2bc61085f0dd`.
- Fresh detached Git worktree: clean before setup.
- Python: 3.14.4.
- Java: 25 LTS; Java compilation target remains 21.
- Maven: 3.9.15.
- Temporal CLI: 1.9.1; local development server: 1.32.0.
- Temporal Java SDK: 1.40.0.
- Local state: three fresh SQLite databases, one Temporal server, and two
  separate P4 provider processes on isolated loopback ports.

The first clean setup exposed two packaging defects: unspecified package
discovery and undeclared test dependencies. They were corrected in local
commits before this final clean-clone run. No recovery behavior, safety rule,
fault script, or historical evidence was changed.

## Executed checks

| Check | Result |
| --- | --- |
| Editable install using `.[dev]` | PASSED |
| Full Python suite | PASSED: 197 passed, 0 failed |
| Provider-audit and common-harness tests | PASSED: 10 passed, 0 failed |
| Java default suite | PASSED: 4 passed, 0 failed, 5 opt-in service tests skipped |
| Explicit service-backed Java tests | PASSED: 2 passed, 0 failed, 0 skipped |
| Release-document local-link check | PASSED |
| Manifest-required-file check | PASSED |

Skipped Java tests remain skipped in the default suite because they require
explicit service properties. The two required service-backed tests were then
run explicitly against the fresh local Temporal service and P4 provider.

## Witness result

Both arms used the same `p4-shared-fault-script-v1` fault contract and matching
graph hash `caefd129b255701ca8087c06610dca85749419d629bfacdadfb3fd17e5756c12`.
They also used the same root logical operation ID.

| Metric | EffectGuard | Temporal |
| --- | ---: | ---: |
| Terminal outcome | `RECOVERED` | `RECOVERED` |
| Retry attempts | 1 | 1 |
| Provider submissions | 2 | 2 |
| Provider verifications | 2 | 2 |
| Actual descendant effects | 1 | 1 |
| Evaluator validity | valid | valid |

Separate provider audit ledgers recorded the scripted pre-commit failure,
subsequent commit with withheld acknowledgement, receipt resolution, and
verification. The machine-readable summary and audit hashes are in
`results/p4/release-candidate-clean-clone-v1/clean_clone_verification.json`.

## Boundaries

This verifies only the one development witness. Restart, provider interruption,
deadline, retry-exhaustion, and broader fault-family claims remain outside the
verified scope. No independent review, sealed benchmark, or confirmatory P4
experiment has occurred.
