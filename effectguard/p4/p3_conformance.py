from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SemanticGapConformance:
    case_id: str
    claimed_positive_semantic_gap: bool
    graph_descendant_count: int
    semantic_invalidated_count: int
    actual_semantic_gap: int
    conforms: bool
    reason: str


def verify_claimed_semantic_gap(
    *,
    case_id: str,
    claimed_positive_semantic_gap: bool,
    graph_descendant_count: int,
    semantic_invalidated_count: int,
) -> SemanticGapConformance:
    actual_semantic_gap = max(0, graph_descendant_count - semantic_invalidated_count)
    conforms = not claimed_positive_semantic_gap or actual_semantic_gap > 0
    reason = (
        "claimed positive semantic gap agrees with the executed dynamic graph"
        if conforms
        else "claimed positive semantic gap is absent from the executed dynamic graph"
    )
    return SemanticGapConformance(
        case_id,
        claimed_positive_semantic_gap,
        graph_descendant_count,
        semantic_invalidated_count,
        actual_semantic_gap,
        conforms,
        reason,
    )
