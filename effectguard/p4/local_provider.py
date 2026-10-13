"""A local, durable external-effect service for P4 fault-injection tests.

This is intentionally a research adapter, not a third-party production
integration. It owns a separate SQLite database and exposes only a local HTTP
interface to clients, allowing restart and authoritative-state tests without
giving the recovery runtime database access.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sqlite3
from threading import Thread
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from ..models import EffectClass, ObservedStatus


class ProviderError(RuntimeError):
    """Base error raised by the local provider."""


class ProviderConflictError(ProviderError):
    """Raised for conflicting decisive outcomes."""


class ProviderTransientError(ProviderError):
    """A deterministic provider-owned transport failure before commitment."""


@dataclass(frozen=True)
class FaultScript:
    """Versioned development-only external fault contract.

    The script is provider-owned: runtimes observe failures but cannot inspect
    or alter the remaining schedule.
    """

    scenario_id: str
    version: str = "p4-shared-fault-script-v1"
    submit_failures_before_commit: int = 0
    lose_acknowledgement_after_commit: bool = False


@dataclass(frozen=True)
class ProviderAuditEvent:
    sequence: int
    event: str
    logical_operation_id: str | None
    detail: str


@dataclass(frozen=True)
class ProviderEffect:
    logical_operation_id: str
    idempotency_key: str
    effect_class: EffectClass
    observed_status: ObservedStatus
    provider_reference: str
    supports_compensation: bool
    compensated: bool = False


@dataclass(frozen=True)
class SubmissionAcknowledgement:
    acknowledged: bool
    timed_out: bool
    duplicate: bool
    effect: ProviderEffect


def _effect_payload(effect: ProviderEffect) -> dict[str, object]:
    return {
        "logical_operation_id": effect.logical_operation_id,
        "idempotency_key": effect.idempotency_key,
        "effect_class": effect.effect_class.value,
        "observed_status": effect.observed_status.value,
        "provider_reference": effect.provider_reference,
        "supports_compensation": effect.supports_compensation,
        "compensated": effect.compensated,
    }


def _effect_from_payload(payload: dict[str, Any]) -> ProviderEffect:
    return ProviderEffect(
        logical_operation_id=str(payload["logical_operation_id"]),
        idempotency_key=str(payload["idempotency_key"]),
        effect_class=EffectClass(str(payload["effect_class"])),
        observed_status=ObservedStatus(str(payload["observed_status"])),
        provider_reference=str(payload["provider_reference"]),
        supports_compensation=bool(payload["supports_compensation"]),
        compensated=bool(payload.get("compensated", False)),
    )


class LocalEffectProvider:
    """Provider-owned state with idempotency, delayed resolution, and restart safety."""

    def __init__(self, database_path: str | Path, *, fault_script: FaultScript | None = None) -> None:
        self.database_path = Path(database_path)
        self._connection = sqlite3.connect(self.database_path, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._fault_script = fault_script
        self._remaining_submit_failures = fault_script.submit_failures_before_commit if fault_script else 0
        self._connection.execute("PRAGMA journal_mode=WAL")
        self._connection.execute("PRAGMA synchronous=FULL")
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS provider_effects (
                logical_operation_id TEXT PRIMARY KEY,
                idempotency_key TEXT NOT NULL UNIQUE,
                effect_class TEXT NOT NULL,
                observed_status TEXT NOT NULL,
                provider_reference TEXT NOT NULL UNIQUE,
                supports_compensation INTEGER NOT NULL,
                compensated INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS provider_audit (
                sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                event TEXT NOT NULL,
                logical_operation_id TEXT,
                detail TEXT NOT NULL
            );
            """
        )
        self._connection.commit()
        if fault_script:
            self._audit("fault_script_loaded", None, f"{fault_script.version}:{fault_script.scenario_id}")

    def close(self) -> None:
        self._connection.close()

    def submit(
        self,
        *,
        logical_operation_id: str,
        idempotency_key: str,
        effect_class: EffectClass,
        supports_compensation: bool,
        acknowledge: bool = True,
    ) -> SubmissionAcknowledgement:
        """Commit an external effect as UNKNOWN, optionally withholding its ack."""

        self._audit("submit_requested", logical_operation_id, idempotency_key)
        if self._remaining_submit_failures:
            self._remaining_submit_failures -= 1
            self._audit("submit_failed_before_commit", logical_operation_id, "scripted retryable transport failure")
            raise ProviderTransientError("scripted retryable transport failure before commitment")
        existing = self._lookup_by_key(idempotency_key)
        if existing is not None:
            self._audit("submit_duplicate", logical_operation_id, idempotency_key)
            return SubmissionAcknowledgement(acknowledge, not acknowledge, True, existing)
        existing = self.verify(logical_operation_id)
        if existing is not None:
            raise ProviderConflictError(f"logical operation uses a different idempotency key: {logical_operation_id}")
        effect = ProviderEffect(
            logical_operation_id=logical_operation_id,
            idempotency_key=idempotency_key,
            effect_class=effect_class,
            observed_status=ObservedStatus.UNKNOWN,
            provider_reference=f"local-provider:{logical_operation_id}",
            supports_compensation=supports_compensation,
        )
        self._connection.execute(
            """
            INSERT INTO provider_effects (
                logical_operation_id, idempotency_key, effect_class, observed_status,
                provider_reference, supports_compensation, compensated
            ) VALUES (?, ?, ?, ?, ?, ?, 0)
            """,
            (
                effect.logical_operation_id,
                effect.idempotency_key,
                effect.effect_class.value,
                effect.observed_status.value,
                effect.provider_reference,
                int(effect.supports_compensation),
            ),
        )
        self._connection.commit()
        self._audit("effect_committed", logical_operation_id, effect.provider_reference)
        lost_ack = bool(self._fault_script and self._fault_script.lose_acknowledgement_after_commit)
        if lost_ack:
            self._audit("acknowledgement_withheld", logical_operation_id, "scripted after-commit timeout")
        return SubmissionAcknowledgement(acknowledge and not lost_ack, not acknowledge or lost_ack, False, effect)

    def resolve(self, logical_operation_id: str, observed_status: ObservedStatus) -> ProviderEffect:
        """Resolve a delayed outcome; conflicting decisive outcomes are rejected."""

        effect = self.verify_required(logical_operation_id)
        decisive = {ObservedStatus.SUCCESS, ObservedStatus.FAILURE}
        if effect.observed_status in decisive and observed_status in decisive and effect.observed_status is not observed_status:
            raise ProviderConflictError(f"conflicting decisive provider outcome: {logical_operation_id}")
        self._connection.execute(
            "UPDATE provider_effects SET observed_status = ? WHERE logical_operation_id = ?",
            (observed_status.value, logical_operation_id),
        )
        self._connection.commit()
        self._audit("receipt_resolved", logical_operation_id, observed_status.value)
        return self.verify_required(logical_operation_id)

    def compensate(self, logical_operation_id: str) -> ProviderEffect:
        self._audit("compensation_requested", logical_operation_id, "")
        effect = self.verify_required(logical_operation_id)
        if not effect.supports_compensation:
            raise ProviderError(f"compensation unsupported: {logical_operation_id}")
        if effect.observed_status is not ObservedStatus.SUCCESS:
            raise ProviderError(f"cannot compensate non-successful effect: {logical_operation_id}")
        self._connection.execute(
            "UPDATE provider_effects SET compensated = 1 WHERE logical_operation_id = ?",
            (logical_operation_id,),
        )
        self._connection.commit()
        self._audit("effect_compensated", logical_operation_id, "")
        return self.verify_required(logical_operation_id)

    def verify(self, logical_operation_id: str) -> ProviderEffect | None:
        self._audit("verification_requested", logical_operation_id, "")
        row = self._connection.execute(
            "SELECT * FROM provider_effects WHERE logical_operation_id = ?",
            (logical_operation_id,),
        ).fetchone()
        return self._effect_from_row(row) if row else None

    def audit_events(self) -> tuple[ProviderAuditEvent, ...]:
        rows = self._connection.execute("SELECT * FROM provider_audit ORDER BY sequence").fetchall()
        return tuple(ProviderAuditEvent(int(row["sequence"]), str(row["event"]), row["logical_operation_id"], str(row["detail"])) for row in rows)

    def _audit(self, event: str, logical_operation_id: str | None, detail: str) -> None:
        self._connection.execute(
            "INSERT INTO provider_audit (event, logical_operation_id, detail) VALUES (?, ?, ?)",
            (event, logical_operation_id, detail),
        )
        self._connection.commit()

    def verify_required(self, logical_operation_id: str) -> ProviderEffect:
        effect = self.verify(logical_operation_id)
        if effect is None:
            raise ProviderError(f"unknown logical operation: {logical_operation_id}")
        return effect

    def _lookup_by_key(self, idempotency_key: str) -> ProviderEffect | None:
        row = self._connection.execute(
            "SELECT * FROM provider_effects WHERE idempotency_key = ?",
            (idempotency_key,),
        ).fetchone()
        return self._effect_from_row(row) if row else None

    @staticmethod
    def _effect_from_row(row: sqlite3.Row) -> ProviderEffect:
        return ProviderEffect(
            logical_operation_id=str(row["logical_operation_id"]),
            idempotency_key=str(row["idempotency_key"]),
            effect_class=EffectClass(row["effect_class"]),
            observed_status=ObservedStatus(row["observed_status"]),
            provider_reference=str(row["provider_reference"]),
            supports_compensation=bool(row["supports_compensation"]),
            compensated=bool(row["compensated"]),
        )


class _ProviderRequestHandler(BaseHTTPRequestHandler):
    server: "LocalProviderServer"

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/audit":
            self._respond(200, {"events": [event.__dict__ for event in self.server.provider.audit_events()]})
            return
        if not self.path.startswith("/verify/"):
            self._respond(404, {"error": "unknown endpoint"})
            return
        logical_operation_id = self.path.removeprefix("/verify/")
        effect = self.server.provider.verify(logical_operation_id)
        if effect is None:
            self._respond(404, {"error": "effect not found"})
            return
        self._respond(200, _effect_payload(effect))

    def do_POST(self) -> None:  # noqa: N802
        try:
            payload = self._read_payload()
            if self.path == "/submit":
                acknowledgement = self.server.provider.submit(
                    logical_operation_id=str(payload["logical_operation_id"]),
                    idempotency_key=str(payload["idempotency_key"]),
                    effect_class=EffectClass(str(payload["effect_class"])),
                    supports_compensation=bool(payload["supports_compensation"]),
                    acknowledge=bool(payload.get("acknowledge", True)),
                )
                self._respond(200, {"acknowledged": acknowledgement.acknowledged, "timed_out": acknowledgement.timed_out, "duplicate": acknowledgement.duplicate, "effect": _effect_payload(acknowledgement.effect)})
                return
            if self.path == "/resolve":
                effect = self.server.provider.resolve(str(payload["logical_operation_id"]), ObservedStatus(str(payload["observed_status"])))
                self._respond(200, _effect_payload(effect))
                return
            if self.path == "/compensate":
                effect = self.server.provider.compensate(str(payload["logical_operation_id"]))
                self._respond(200, _effect_payload(effect))
                return
            self._respond(404, {"error": "unknown endpoint"})
        except ProviderTransientError as error:
            self._respond(503, {"error": str(error), "retryable": True})
        except (KeyError, ValueError, ProviderError) as error:
            self._respond(409, {"error": str(error)})

    def _read_payload(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def _respond(self, status: int, payload: dict[str, object]) -> None:
        body = json.dumps(payload, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_: object) -> None:
        """Keep deterministic test output free of request logs."""


class LocalProviderServer(ThreadingHTTPServer):
    """HTTP service wrapper; it can run in a separate local process via ``serve``."""

    def __init__(self, address: tuple[str, int], provider: LocalEffectProvider) -> None:
        super().__init__(address, _ProviderRequestHandler)
        self.provider = provider


class LocalProviderClient:
    """Recovery/evaluator-facing client that cannot access provider SQLite state."""

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    def submit(self, **payload: object) -> SubmissionAcknowledgement:
        response = self._post("/submit", payload)
        return SubmissionAcknowledgement(
            acknowledged=bool(response["acknowledged"]),
            timed_out=bool(response["timed_out"]),
            duplicate=bool(response["duplicate"]),
            effect=_effect_from_payload(response["effect"]),
        )

    def resolve(self, logical_operation_id: str, observed_status: ObservedStatus) -> ProviderEffect:
        return _effect_from_payload(self._post("/resolve", {"logical_operation_id": logical_operation_id, "observed_status": observed_status.value}))

    def compensate(self, logical_operation_id: str) -> ProviderEffect:
        return _effect_from_payload(self._post("/compensate", {"logical_operation_id": logical_operation_id}))

    def verify(self, logical_operation_id: str) -> ProviderEffect | None:
        try:
            with urlopen(f"{self.base_url}/verify/{logical_operation_id}", timeout=5) as response:
                return _effect_from_payload(json.loads(response.read().decode("utf-8")))
        except HTTPError as error:
            if error.code == 404:
                return None
            raise ProviderError(f"provider verify failed with HTTP {error.code}") from error

    def _post(self, path: str, payload: dict[str, object]) -> dict[str, Any]:
        request = Request(
            f"{self.base_url}{path}",
            data=json.dumps(payload, sort_keys=True).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=5) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            payload = json.loads(error.read().decode("utf-8"))
            if error.code == 503:
                raise ProviderTransientError(str(payload.get("error", "retryable provider failure"))) from error
            raise ProviderError(str(payload.get("error", f"HTTP {error.code}"))) from error


class RunningLocalProvider:
    """Test helper that starts the service on an ephemeral local port."""

    def __init__(self, database_path: str | Path) -> None:
        self.provider = LocalEffectProvider(database_path)
        self.server = LocalProviderServer(("127.0.0.1", 0), self.provider)
        self._thread = Thread(target=self.server.serve_forever, daemon=True)

    def __enter__(self) -> LocalProviderClient:
        self._thread.start()
        host, port = self.server.server_address
        return LocalProviderClient(f"http://{host}:{port}")

    def __exit__(self, *_: object) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.provider.close()
        self._thread.join(timeout=5)


def serve_local_provider(
    database_path: str | Path,
    *,
    host: str = "127.0.0.1",
    port: int = 8765,
    fault_script: FaultScript | None = None,
) -> None:
    """Run the provider as a standalone local process until interrupted."""

    provider = LocalEffectProvider(database_path, fault_script=fault_script)
    server = LocalProviderServer((host, port), provider)
    try:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
    finally:
        server.server_close()
        provider.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the P4 local effect provider")
    parser.add_argument("--database", required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8765, type=int)
    parser.add_argument("--fault-script", type=Path)
    arguments = parser.parse_args()
    script = FaultScript(**json.loads(arguments.fault_script.read_text(encoding="utf-8"))) if arguments.fault_script else None
    serve_local_provider(arguments.database, host=arguments.host, port=arguments.port, fault_script=script)


if __name__ == "__main__":
    main()
