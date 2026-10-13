# Reproducibility Guide

## Supported target

Reproduce only the development-only two-arm scripted retry and
lost-acknowledgement witness. This history-isolated branch deliberately omits
the historical raw reconciliation trace; a reviewer generates fresh provider
audit evidence during the procedure below.

## Requirements

- Python 3.10 or later; the original environment used Python 3.13.5.
- Java 21; `temporal-baseline/pom.xml` compiles with release 21. The original
  environment ran Java 25, which is not the portability target.
- Maven 3.9 or later; original environment: Maven 3.9.15.
- Temporal CLI development server; original environment reported CLI 1.9.1
  and server 1.32.0.
- SQLite, using fresh file-backed databases. No external network or paid model
  provider is needed.
- Available local ports `7245`, `8785`, and `8786`.

The Java baseline pins Temporal SDK 1.40.0 in `temporal-baseline/pom.xml`.
Python has no runtime dependency beyond the standard library; test execution
requires `pytest>=8` as declared in `pyproject.toml`.

## Isolated setup

From a reviewed source snapshot containing the manifest artifacts:

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'
cd temporal-baseline && mvn -q test && cd ..
temporal server start-dev --ip 127.0.0.1 --port 7245
```

In two separate terminals, start isolated providers with separate SQLite files:

```bash
PYTHONPATH=. .venv/bin/python -m effectguard.p4.local_provider \
  --database "${TMPDIR:-/tmp}/effectguard-review-eg.sqlite" \
  --port 8785 \
  --fault-script experiments/p4/shared_fault_script_v1.json

PYTHONPATH=. .venv/bin/python -m effectguard.p4.local_provider \
  --database "${TMPDIR:-/tmp}/effectguard-review-temporal.sqlite" \
  --port 8786 \
  --fault-script experiments/p4/shared_fault_script_v1.json
```

Then run the paired witness:

```bash
PYTHONPATH=. .venv/bin/python -m effectguard.p4.common_execution \
  --task-id travel_positive_gap_success \
  --pair-namespace reviewer-scripted \
  --effectguard-provider-url http://127.0.0.1:8785 \
  --temporal-service-address 127.0.0.1:7245 \
  --temporal-provider-url http://127.0.0.1:8786 \
  --output "${TMPDIR:-/tmp}/effectguard-review-witness.json"
```

Inspect the providers' `GET /audit` endpoints and compare the physical attempts,
receipt transitions, and evaluator outcome against `EXPECTED_RESULTS.md`. Stop
the Temporal server and both providers afterward. Typical runtime is under five
minutes on a laptop; reserve roughly 2 GB RAM for the JVM, Temporal service,
and two provider processes.

## Verification status

A fresh detached worktree at the reviewed runtime-source commit successfully
installed with `.[dev]`, passed the Python and Java checks, and reproduced the
documented witness using fresh Temporal and provider state. Exact results,
versions, and audit hashes are in
`paper/release_candidate/CLEAN_CLONE_VERIFICATION_REPORT.md`.
