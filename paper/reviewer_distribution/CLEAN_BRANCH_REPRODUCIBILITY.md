# Clean Branch Reproducibility

## Required software

- Python 3.11 or later with `venv`.
- Java 17 or later and Maven 3.9 or later.
- Temporal CLI development server compatible with the Java SDK declared in
  `temporal-baseline/pom.xml`.
- `curl` for local-service health checks.

## Clean-checkout procedure

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e '.[dev]'
PYTHONPATH=. .venv/bin/pytest -q \
  tests/test_p4_common_execution.py \
  tests/test_p4_local_provider.py \
  tests/test_p4_unknown_safe_recovery.py
(cd temporal-baseline && mvn -q test)
```

For the real-service witness, follow the exact startup, teardown, and command
sequence in `paper/release_candidate/REPRODUCIBILITY_GUIDE.md`. Use new temporary
SQLite files and unused loopback ports. Do not reuse a provider database or a
Temporal server from a prior run.

## Expected boundary

The witness exercises a scripted retry/lost-acknowledgement case. It is not a
held-out benchmark and does not validate the unimplemented restart and deadline
families. Reviewers should compare actual provider audit evidence and evaluator
outcomes, not terminal status alone.

## Fresh verification record

A clean local clone of the orphan branch passed the three focused Python test
modules (20 tests). The default Java suite passed four unit tests and skipped
five service-dependent tests before services were started. With fresh local
Temporal and provider services, the explicit service-backed tests passed and the
paired witness reported `RECOVERED` for both arms, matching graph hashes, four
logical recovery actions, two provider submissions, two verifications, one
retry, one materialized descendant effect, and valid independent evaluator
verdicts. The provider audit hashes are recorded only in the local verification
run; raw traces are intentionally not committed to this reviewer snapshot.
