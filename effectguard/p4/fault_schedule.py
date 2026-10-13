"""Versioned public fault schedule for development-only common executions."""

from __future__ import annotations

from dataclasses import dataclass

from .benchmark import DevelopmentScenario


@dataclass(frozen=True)
class DevelopmentFaultSchedule:
    version: str
    root_resolution: str
    duplicate_delivery: bool
    compensation_failure: bool
    evidence_deadline_expired: bool
    retry_budget: int
    activity_timeout_ms: int
    worker_restart: bool
    provider_interruption: bool

    @classmethod
    def from_scenario(cls, scenario: DevelopmentScenario) -> "DevelopmentFaultSchedule":
        return cls(
            version="p4-development-fault-schedule-v1",
            root_resolution=scenario.resolved_status.value,
            duplicate_delivery=scenario.duplicate_delivery,
            compensation_failure=scenario.compensation_fails,
            evidence_deadline_expired=scenario.evidence_deadline_expired,
            retry_budget=2,
            activity_timeout_ms=10_000,
            worker_restart=scenario.restart_interrupted,
            provider_interruption=False,
        )
