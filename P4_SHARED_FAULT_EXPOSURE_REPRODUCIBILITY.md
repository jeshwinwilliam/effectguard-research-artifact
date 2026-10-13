# P4 Shared Fault Exposure Reproducibility

## Provider Audit Test

```bash
cd /path/to/EffectGuard
PYTHONPATH=. .venv/bin/pytest -q tests/test_p4_local_provider.py tests/test_p4_common_execution.py
```

## Run the Provider with a Script

```bash
PYTHONPATH=. .venv/bin/python -m effectguard.p4.local_provider \
  --database "${TMPDIR:-/tmp}/effectguard-shared-fault.sqlite" \
  --port 8784 \
  --fault-script experiments/p4/shared_fault_script_v1.json
```

The authoritative development audit is available from `GET /audit`. A first
submit receives HTTP `503` before any effect commit; the next submit commits
and reports a withheld acknowledgement. This is not a completed paired study.

To reproduce the verified two-arm witness, start a fresh Temporal development
service and two fresh providers using the same script, then run:

```bash
PYTHONPATH=. .venv/bin/python -m effectguard.p4.common_execution \
  --task-id travel_positive_gap_success \
  --pair-namespace two-arm-scripted \
  --effectguard-provider-url http://127.0.0.1:8785 \
  --temporal-service-address 127.0.0.1:7245 \
  --temporal-provider-url http://127.0.0.1:8786 \
  --output "${TMPDIR:-/tmp}/effectguard-two-arm-scripted.json"
```
