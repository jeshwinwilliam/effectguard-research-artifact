from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from ..models import EffectClass, ObservedStatus
from .models import ActionDescriptor, EffectReceipt, ProviderCapabilities, RecoveryRequest


@dataclass(frozen=True)
class DevelopmentAction:
    descriptor: ActionDescriptor
    parents: tuple[str, ...]


@dataclass(frozen=True)
class DevelopmentScenario:
    task_id: str
    domain: str
    fault: str
    claimed_positive_semantic_gap: bool
    semantic_gap_applicable: bool
    root_receipt: EffectReceipt
    resolved_status: ObservedStatus
    actions: tuple[DevelopmentAction, ...]
    expected_validity: dict[str, str]
    required_invariants: tuple[str, ...]
    compensation_fails: bool = False
    restart_interrupted: bool = False
    duplicate_delivery: bool = False
    evidence_deadline_expired: bool = False

    def request(self, *, resolved: bool) -> RecoveryRequest:
        receipt = EffectReceipt(
            logical_operation_id=self.root_receipt.logical_operation_id,
            effect_class=self.root_receipt.effect_class,
            observed_status=self.resolved_status if resolved else self.root_receipt.observed_status,
            provider_reference=self.root_receipt.provider_reference,
            idempotency_key=self.root_receipt.idempotency_key,
            capabilities=self.root_receipt.capabilities,
        )
        return RecoveryRequest(
            workflow_id=self.task_id,
            actions=tuple(action.descriptor for action in self.actions),
            receipts=(receipt,),
            required_invariants=self.required_invariants,
            evidence_deadline_expired=self.evidence_deadline_expired and resolved,
        )

    def graph_descendants(self) -> tuple[str, ...]:
        children: dict[str, set[str]] = {}
        for action in self.actions:
            for parent in action.parents:
                children.setdefault(parent, set()).add(action.descriptor.action_id)
        remaining = list(children.get(self.root_receipt.logical_operation_id, set()))
        descendants: set[str] = set()
        while remaining:
            action_id = remaining.pop()
            if action_id in descendants:
                continue
            descendants.add(action_id)
            remaining.extend(children.get(action_id, set()))
        return tuple(sorted(descendants))

    def semantic_invalidated_actions(self) -> tuple[str, ...]:
        descendants = set(self.graph_descendants())
        return tuple(sorted(action_id for action_id, result in self.expected_validity.items() if result == "INVALID" and action_id in descendants))


@dataclass(frozen=True)
class SemanticGapValidation:
    task_id: str
    graph_descendants: tuple[str, ...]
    semantic_invalidated_actions: tuple[str, ...]
    semantic_gap: int
    conforms: bool
    reason: str


@dataclass(frozen=True)
class DevelopmentBenchmark:
    benchmark_id: str
    kind: str
    authorship: str
    source_path: Path
    scenarios: tuple[DevelopmentScenario, ...]


def _capabilities(payload: dict[str, object], *, compensation: bool | None = None) -> ProviderCapabilities:
    return ProviderCapabilities(
        supports_idempotency=bool(payload.get("idempotency", True)),
        supports_deduplication_lookup=bool(payload.get("deduplication", True)),
        supports_verification=bool(payload.get("verification", True)),
        supports_compensation=bool(payload.get("compensation", compensation if compensation is not None else False)),
    )


def _effect_class(value: str) -> EffectClass:
    return EffectClass(value)


def _observed_status(value: str) -> ObservedStatus:
    return ObservedStatus(value)


def load_development_benchmark(path: str | Path) -> DevelopmentBenchmark:
    source_path = Path(path)
    payload = json.loads(source_path.read_text(encoding="utf-8"))
    scenarios: list[DevelopmentScenario] = []
    for item in payload["scenarios"]:
        root = item["root_effect"]
        root_capabilities = _capabilities(root, compensation=False)
        root_receipt = EffectReceipt(
            logical_operation_id=str(root["logical_operation_id"]),
            effect_class=_effect_class(str(root["effect_class"])),
            observed_status=_observed_status(str(root["initial_status"])),
            provider_reference=f"development:{item['task_id']}:{root['logical_operation_id']}",
            idempotency_key=f"development:{item['task_id']}:{root['logical_operation_id']}",
            capabilities=root_capabilities,
        )
        actions = tuple(
            DevelopmentAction(
                descriptor=ActionDescriptor(
                    action_id=str(action["action_id"]),
                    logical_operation_id=str(action["logical_operation_id"]),
                    effect_class=_effect_class(str(action["effect_class"])),
                    conflicts_with_effects=tuple(str(value) for value in action.get("conflicts_with", [])),
                    capabilities=_capabilities(action, compensation=bool(action.get("compensation", False))),
                ),
                parents=tuple(str(value) for value in action.get("parents", [])),
            )
            for action in item["actions"]
        )
        scenarios.append(
            DevelopmentScenario(
                task_id=str(item["task_id"]),
                domain=str(item["domain"]),
                fault=str(item["fault"]),
                claimed_positive_semantic_gap=bool(item["claimed_positive_semantic_gap"]),
                semantic_gap_applicable=bool(item["semantic_gap_applicable"]),
                root_receipt=root_receipt,
                resolved_status=_observed_status(str(root["resolved_status"])),
                actions=actions,
                expected_validity={str(key): str(value) for key, value in item["expected_validity"].items()},
                required_invariants=tuple(str(value) for value in item["required_invariants"]),
                compensation_fails=bool(item.get("compensation_fails", False)),
                restart_interrupted=bool(item.get("restart_interrupted", False)),
                duplicate_delivery=bool(item.get("duplicate_delivery", False)),
                evidence_deadline_expired=bool(item.get("evidence_deadline_expired", False)),
            )
        )
    return DevelopmentBenchmark(
        benchmark_id=str(payload["benchmark_id"]),
        kind=str(payload["kind"]),
        authorship=str(payload["authorship"]),
        source_path=source_path,
        scenarios=tuple(scenarios),
    )


def validate_semantic_gap(scenario: DevelopmentScenario) -> SemanticGapValidation:
    descendants = scenario.graph_descendants()
    invalidated = scenario.semantic_invalidated_actions()
    gap = len(descendants) - len(invalidated)
    if not scenario.semantic_gap_applicable:
        return SemanticGapValidation(scenario.task_id, descendants, invalidated, gap, True, "semantic gap is not defined for unresolved evidence")
    conforms = gap > 0 if scenario.claimed_positive_semantic_gap else gap == 0
    reason = "graph and semantic sets agree with the declared development label" if conforms else "declared development label disagrees with the actual P4 graph"
    return SemanticGapValidation(scenario.task_id, descendants, invalidated, gap, conforms, reason)


def validate_development_benchmark(benchmark: DevelopmentBenchmark) -> tuple[SemanticGapValidation, ...]:
    if benchmark.kind != "development_only":
        raise ValueError("P4 development benchmark must be labeled development_only")
    if benchmark.authorship != "codex_authored_not_independent":
        raise ValueError("development benchmark authorship must remain explicit")
    expected_domains = {"procurement", "travel", "cloud", "fulfillment"}
    present_domains = {scenario.domain for scenario in benchmark.scenarios}
    if present_domains != expected_domains:
        raise ValueError(f"development benchmark domains differ: {present_domains}")
    faults = {scenario.fault for scenario in benchmark.scenarios}
    required_faults = {
        "UNKNOWN_TO_SUCCESS",
        "UNKNOWN_TO_FAILURE",
        "UNKNOWN_TIMEOUT",
        "UNKNOWN_IRREVERSIBLE",
        "DUPLICATE_DELIVERY",
        "COMPENSATION_FAILURE",
        "CRASH_RESTART",
    }
    if not required_faults <= faults:
        raise ValueError(f"development benchmark fault coverage is incomplete: {required_faults - faults}")
    reports = tuple(validate_semantic_gap(scenario) for scenario in benchmark.scenarios)
    failed = [report.task_id for report in reports if not report.conforms]
    if failed:
        raise ValueError(f"semantic-gap conformance failed for: {failed}")
    return reports
