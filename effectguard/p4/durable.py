"""Crash-safe local receipt persistence for P4 development experiments.

This module intentionally has no dependency on the recovery runtime. It is a
small durable boundary for tests and future adapters, not a provider exactly-
once guarantee.
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
import json
from pathlib import Path
import sqlite3
from typing import Iterator

from ..models import EffectClass, ObservedStatus
from .models import EffectReceipt, ProviderCapabilities


class DurableReceiptError(RuntimeError):
    """Base error for durable receipt operations."""


class DuplicateReceiptError(DurableReceiptError):
    """Raised when a logical operation is submitted more than once."""


class ConflictingReceiptOutcomeError(DurableReceiptError):
    """Raised when decisive provider outcomes disagree for one operation."""


class InjectedDurableStoreFailure(DurableReceiptError):
    """Deterministic development-only crash boundary before transaction commit."""


@dataclass(frozen=True)
class ReceiptTransition:
    sequence: int
    workflow_id: str
    logical_operation_id: str
    event: str
    previous_status: ObservedStatus | None
    new_status: ObservedStatus
    detail: str


def _capabilities_payload(capabilities: ProviderCapabilities) -> str:
    return json.dumps(
        {
            "supports_idempotency": capabilities.supports_idempotency,
            "supports_deduplication_lookup": capabilities.supports_deduplication_lookup,
            "supports_verification": capabilities.supports_verification,
            "supports_compensation": capabilities.supports_compensation,
        },
        sort_keys=True,
    )


def _capabilities_from_payload(payload: str) -> ProviderCapabilities:
    values = json.loads(payload)
    return ProviderCapabilities(
        supports_idempotency=bool(values["supports_idempotency"]),
        supports_deduplication_lookup=bool(values["supports_deduplication_lookup"]),
        supports_verification=bool(values["supports_verification"]),
        supports_compensation=bool(values["supports_compensation"]),
    )


class DurableReceiptStore:
    """SQLite-backed receipt store with an append-only transition history.

    Each write is one SQLite transaction. A transition from UNKNOWN to a
    decisive observation is allowed; conflicting decisive observations are
    rejected rather than silently rewritten.
    """

    def __init__(self, database_path: str | Path, *, fail_after_writes: int | None = None) -> None:
        self.database_path = Path(database_path)
        self._fail_after_writes = fail_after_writes
        self._write_count = 0
        self._connection = sqlite3.connect(self.database_path)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA journal_mode=WAL")
        self._connection.execute("PRAGMA synchronous=FULL")
        self._initialize()

    def close(self) -> None:
        self._connection.close()

    def __enter__(self) -> "DurableReceiptStore":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def set_failure_after_writes(self, write_count: int | None) -> None:
        """Inject one deterministic pre-commit failure after the given writes."""

        self._fail_after_writes = write_count
        self._write_count = 0

    def _initialize(self) -> None:
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS receipts (
                workflow_id TEXT NOT NULL,
                logical_operation_id TEXT NOT NULL,
                effect_class TEXT NOT NULL,
                observed_status TEXT NOT NULL,
                provider_reference TEXT,
                idempotency_key TEXT,
                capabilities_json TEXT NOT NULL,
                PRIMARY KEY (workflow_id, logical_operation_id)
            );
            CREATE TABLE IF NOT EXISTS receipt_transitions (
                sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                workflow_id TEXT NOT NULL,
                logical_operation_id TEXT NOT NULL,
                event TEXT NOT NULL,
                previous_status TEXT,
                new_status TEXT NOT NULL,
                detail TEXT NOT NULL
            );
            """
        )
        self._connection.commit()

    @contextmanager
    def _transaction(self) -> Iterator[sqlite3.Cursor]:
        cursor = self._connection.cursor()
        try:
            cursor.execute("BEGIN IMMEDIATE")
            yield cursor
            self._maybe_fail_before_commit()
            self._connection.commit()
        except Exception:
            self._connection.rollback()
            raise
        finally:
            cursor.close()

    def _maybe_fail_before_commit(self) -> None:
        if self._fail_after_writes is not None and self._write_count >= self._fail_after_writes:
            self._fail_after_writes = None
            raise InjectedDurableStoreFailure("deterministic durable-store failure before commit")
        self._write_count += 1

    def persist_submission(self, workflow_id: str, receipt: EffectReceipt, *, detail: str = "submission accepted") -> EffectReceipt:
        """Atomically persist one initial receipt and its audit transition."""

        try:
            with self._transaction() as cursor:
                cursor.execute(
                    """
                    INSERT INTO receipts (
                        workflow_id, logical_operation_id, effect_class, observed_status,
                        provider_reference, idempotency_key, capabilities_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        workflow_id,
                        receipt.logical_operation_id,
                        receipt.effect_class.value,
                        receipt.observed_status.value,
                        receipt.provider_reference,
                        receipt.idempotency_key,
                        _capabilities_payload(receipt.capabilities),
                    ),
                )
                self._append_transition(cursor, workflow_id, receipt.logical_operation_id, "submission_persisted", None, receipt.observed_status, detail)
        except sqlite3.IntegrityError as error:
            raise DuplicateReceiptError(f"duplicate logical operation: {receipt.logical_operation_id}") from error
        return receipt

    def resolve_observation(
        self,
        workflow_id: str,
        logical_operation_id: str,
        observed_status: ObservedStatus,
        *,
        provider_reference: str | None = None,
        detail: str = "provider observation resolved",
    ) -> EffectReceipt:
        """Persist a delayed provider observation without allowing contradiction."""

        existing = self.load_receipt(workflow_id, logical_operation_id)
        if existing is None:
            raise DurableReceiptError(f"unknown logical operation: {logical_operation_id}")
        decisive = {ObservedStatus.SUCCESS, ObservedStatus.FAILURE}
        if existing.observed_status in decisive and observed_status in decisive and existing.observed_status is not observed_status:
            raise ConflictingReceiptOutcomeError(f"conflicting outcome for logical operation: {logical_operation_id}")
        updated = EffectReceipt(
            logical_operation_id=existing.logical_operation_id,
            effect_class=existing.effect_class,
            observed_status=observed_status,
            provider_reference=provider_reference or existing.provider_reference,
            idempotency_key=existing.idempotency_key,
            capabilities=existing.capabilities,
        )
        with self._transaction() as cursor:
            cursor.execute(
                """
                UPDATE receipts
                SET observed_status = ?, provider_reference = ?
                WHERE workflow_id = ? AND logical_operation_id = ?
                """,
                (updated.observed_status.value, updated.provider_reference, workflow_id, logical_operation_id),
            )
            self._append_transition(
                cursor,
                workflow_id,
                logical_operation_id,
                "observation_resolved",
                existing.observed_status,
                updated.observed_status,
                detail,
            )
        return updated

    def load_receipt(self, workflow_id: str, logical_operation_id: str) -> EffectReceipt | None:
        row = self._connection.execute(
            "SELECT * FROM receipts WHERE workflow_id = ? AND logical_operation_id = ?",
            (workflow_id, logical_operation_id),
        ).fetchone()
        return self._receipt_from_row(row) if row else None

    def receipts_for_workflow(self, workflow_id: str) -> tuple[EffectReceipt, ...]:
        rows = self._connection.execute(
            "SELECT * FROM receipts WHERE workflow_id = ? ORDER BY logical_operation_id",
            (workflow_id,),
        ).fetchall()
        return tuple(self._receipt_from_row(row) for row in rows)

    def transition_history(self, workflow_id: str, logical_operation_id: str) -> tuple[ReceiptTransition, ...]:
        rows = self._connection.execute(
            """
            SELECT * FROM receipt_transitions
            WHERE workflow_id = ? AND logical_operation_id = ?
            ORDER BY sequence
            """,
            (workflow_id, logical_operation_id),
        ).fetchall()
        return tuple(
            ReceiptTransition(
                sequence=int(row["sequence"]),
                workflow_id=str(row["workflow_id"]),
                logical_operation_id=str(row["logical_operation_id"]),
                event=str(row["event"]),
                previous_status=ObservedStatus(row["previous_status"]) if row["previous_status"] else None,
                new_status=ObservedStatus(row["new_status"]),
                detail=str(row["detail"]),
            )
            for row in rows
        )

    @staticmethod
    def _receipt_from_row(row: sqlite3.Row) -> EffectReceipt:
        return EffectReceipt(
            logical_operation_id=str(row["logical_operation_id"]),
            effect_class=EffectClass(row["effect_class"]),
            observed_status=ObservedStatus(row["observed_status"]),
            provider_reference=row["provider_reference"],
            idempotency_key=row["idempotency_key"],
            capabilities=_capabilities_from_payload(str(row["capabilities_json"])),
        )

    @staticmethod
    def _append_transition(
        cursor: sqlite3.Cursor,
        workflow_id: str,
        logical_operation_id: str,
        event: str,
        previous_status: ObservedStatus | None,
        new_status: ObservedStatus,
        detail: str,
    ) -> None:
        cursor.execute(
            """
            INSERT INTO receipt_transitions (
                workflow_id, logical_operation_id, event, previous_status,
                new_status, detail
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                workflow_id,
                logical_operation_id,
                event,
                previous_status.value if previous_status else None,
                new_status.value,
                detail,
            ),
        )
