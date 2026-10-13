"""Development-only importer for externally authored WfCommons topology.

The importer intentionally carries only workflow structure. EffectGuard effect
contracts live in a separate synthetic annotation file and cannot be inferred
from scientific task names or performance metadata.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


class WfCommonsImportError(ValueError):
    """Raised when a WfFormat payload is structurally unusable as a DAG."""


@dataclass(frozen=True)
class ImportedTask:
    task_id: str
    name: str
    parents: tuple[str, ...]
    children: tuple[str, ...]


@dataclass(frozen=True)
class ImportedWorkflow:
    workflow_id: str
    source_path: Path
    schema_version: str
    tasks: tuple[ImportedTask, ...]
    topological_order: tuple[str, ...]

    @property
    def task_ids(self) -> tuple[str, ...]:
        return tuple(task.task_id for task in self.tasks)


def load_wfcommons_workflow(path: str | Path) -> ImportedWorkflow:
    """Load WfFormat topology and reject malformed, inconsistent, or cyclic DAGs."""

    source_path = Path(path)
    try:
        payload = json.loads(source_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise WfCommonsImportError(f"cannot read WfCommons JSON: {source_path}") from error

    schema_version = payload.get("schemaVersion")
    workflow = payload.get("workflow")
    specification = workflow.get("specification") if isinstance(workflow, dict) else None
    raw_tasks = specification.get("tasks") if isinstance(specification, dict) else None
    if not isinstance(schema_version, str) or not isinstance(raw_tasks, list) or not raw_tasks:
        raise WfCommonsImportError("WfFormat payload requires schemaVersion and non-empty workflow.specification.tasks")

    tasks: list[ImportedTask] = []
    for raw_task in raw_tasks:
        if not isinstance(raw_task, dict):
            raise WfCommonsImportError("WfFormat tasks must be objects")
        task_id = raw_task.get("id")
        name = raw_task.get("name")
        parents = raw_task.get("parents")
        children = raw_task.get("children")
        if not isinstance(task_id, str) or not task_id or not isinstance(name, str) or not name:
            raise WfCommonsImportError("every WfFormat task requires non-empty id and name")
        if not isinstance(parents, list) or not isinstance(children, list):
            raise WfCommonsImportError(f"task {task_id} requires parents and children lists")
        if any(not isinstance(value, str) or not value for value in parents + children):
            raise WfCommonsImportError(f"task {task_id} has an invalid edge reference")
        if len(set(parents)) != len(parents) or len(set(children)) != len(children):
            raise WfCommonsImportError(f"task {task_id} repeats an edge reference")
        tasks.append(ImportedTask(task_id, name, tuple(parents), tuple(children)))

    index = {task.task_id: task for task in tasks}
    if len(index) != len(tasks):
        raise WfCommonsImportError("WfFormat task identifiers must be unique")
    for task in tasks:
        for parent_id in task.parents:
            parent = index.get(parent_id)
            if parent is None:
                raise WfCommonsImportError(f"task {task.task_id} references missing parent {parent_id}")
            if task.task_id not in parent.children:
                raise WfCommonsImportError(f"edge {parent_id}->{task.task_id} is not reciprocally declared")
        for child_id in task.children:
            child = index.get(child_id)
            if child is None:
                raise WfCommonsImportError(f"task {task.task_id} references missing child {child_id}")
            if task.task_id not in child.parents:
                raise WfCommonsImportError(f"edge {task.task_id}->{child_id} is not reciprocally declared")

    topological_order = _topological_order(tasks)
    workflow_name = payload.get("name")
    if not isinstance(workflow_name, str) or not workflow_name:
        raise WfCommonsImportError("WfFormat payload requires a non-empty name")
    return ImportedWorkflow(workflow_name, source_path, schema_version, tuple(tasks), topological_order)


def _topological_order(tasks: list[ImportedTask]) -> tuple[str, ...]:
    remaining = {task.task_id: set(task.parents) for task in tasks}
    children = {task.task_id: task.children for task in tasks}
    ordered: list[str] = []
    ready = sorted(task_id for task_id, parents in remaining.items() if not parents)
    while ready:
        task_id = ready.pop(0)
        ordered.append(task_id)
        for child_id in children[task_id]:
            remaining[child_id].remove(task_id)
            if not remaining[child_id]:
                ready.append(child_id)
        ready.sort()
    if len(ordered) != len(tasks):
        raise WfCommonsImportError("WfFormat task graph must be acyclic")
    return tuple(ordered)
