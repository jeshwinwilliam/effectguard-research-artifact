"""Synthetic development overlays for externally sourced workflow topology."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from ..models import EffectClass
from .wfcommons import ImportedWorkflow


class EffectAnnotationError(ValueError):
    """Raised when an effect overlay would make an unsupported safety claim."""


@dataclass(frozen=True)
class ExternalEffectAnnotation:
    task_id: str
    effect_type: str
    effect_class: EffectClass
    reversibility: str
    idempotency: str
    verification_capability: str
    compensation_capability: str
    assumption_dependencies: tuple[str, ...]
    unknown_outcome_handling: str
    final_state_invariants: tuple[str, ...]
    evidence_origin: str
    evidence_reference: str | None


@dataclass(frozen=True)
class EffectAnnotationSet:
    topology_id: str
    kind: str
    authorship: str
    annotations: tuple[ExternalEffectAnnotation, ...]


def load_effect_annotations(path: str | Path, topology: ImportedWorkflow) -> EffectAnnotationSet:
    source_path = Path(path)
    try:
        payload = json.loads(source_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise EffectAnnotationError(f"cannot read annotation JSON: {source_path}") from error

    if payload.get("kind") != "development_only_synthetic_effect_overlay":
        raise EffectAnnotationError("external topology annotations must remain a development-only synthetic overlay")
    if payload.get("topology_id") != topology.workflow_id:
        raise EffectAnnotationError("annotation topology_id does not match imported workflow")
    if payload.get("authorship") != "effectguard_synthetic_not_independent":
        raise EffectAnnotationError("annotation authorship must state that it is synthetic and not independent")
    raw_annotations = payload.get("annotations")
    if not isinstance(raw_annotations, list) or not raw_annotations:
        raise EffectAnnotationError("annotation payload requires a non-empty annotations list")

    known_task_ids = set(topology.task_ids)
    annotations: list[ExternalEffectAnnotation] = []
    seen: set[str] = set()
    for raw in raw_annotations:
        if not isinstance(raw, dict):
            raise EffectAnnotationError("each annotation must be an object")
        task_id = _non_empty(raw, "task_id")
        if task_id not in known_task_ids:
            raise EffectAnnotationError(f"annotation targets unknown imported task {task_id}")
        if task_id in seen:
            raise EffectAnnotationError(f"duplicate annotation for imported task {task_id}")
        seen.add(task_id)
        effect_class = EffectClass(_non_empty(raw, "effect_class"))
        evidence_origin = _non_empty(raw, "evidence_origin")
        evidence_reference = raw.get("evidence_reference")
        if evidence_reference is not None and (not isinstance(evidence_reference, str) or not evidence_reference):
            raise EffectAnnotationError("evidence_reference must be a non-empty string when present")
        if effect_class is EffectClass.IRREVERSIBLE and (
            evidence_origin != "independently_supported" or evidence_reference is None
        ):
            raise EffectAnnotationError("irreversible effects require independently supported evidence and a reference")
        unknown_handling = _non_empty(raw, "unknown_outcome_handling")
        if unknown_handling not in {"BLOCK", "DEFER", "UNRESOLVED"}:
            raise EffectAnnotationError("UNKNOWN handling must be BLOCK, DEFER, or UNRESOLVED")
        idempotency = _non_empty(raw, "idempotency")
        if idempotency not in {"DECLARED_SUPPORTED", "NOT_SUPPORTED"}:
            raise EffectAnnotationError("idempotency must be DECLARED_SUPPORTED or NOT_SUPPORTED")
        verification = _non_empty(raw, "verification_capability")
        compensation = _non_empty(raw, "compensation_capability")
        if compensation == "DECLARED_SUPPORTED" and effect_class not in {EffectClass.REVERSIBLE, EffectClass.COMPENSABLE}:
            raise EffectAnnotationError("compensation is only valid for REVERSIBLE or COMPENSABLE effects")
        annotations.append(
            ExternalEffectAnnotation(
                task_id=task_id,
                effect_type=_non_empty(raw, "effect_type"),
                effect_class=effect_class,
                reversibility=_non_empty(raw, "reversibility"),
                idempotency=idempotency,
                verification_capability=verification,
                compensation_capability=compensation,
                assumption_dependencies=tuple(_string_list(raw, "assumption_dependencies")),
                unknown_outcome_handling=unknown_handling,
                final_state_invariants=tuple(_string_list(raw, "final_state_invariants")),
                evidence_origin=evidence_origin,
                evidence_reference=evidence_reference,
            )
        )
    return EffectAnnotationSet(topology.workflow_id, str(payload["kind"]), str(payload["authorship"]), tuple(annotations))


def _non_empty(payload: dict[str, object], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise EffectAnnotationError(f"annotation requires non-empty {key}")
    return value


def _string_list(payload: dict[str, object], key: str) -> list[str]:
    value = payload.get(key)
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        raise EffectAnnotationError(f"annotation requires a string list for {key}")
    return value
