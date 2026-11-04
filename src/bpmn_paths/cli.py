"""Command line interface: ``python -m bpmn_paths FILE``."""

import argparse
import sys
from collections.abc import Sequence

from bpmn_paths.model import BpmnError, ProcessGraph
from bpmn_paths.parser import load_process
from bpmn_paths.paths import PathResult, ProcessPath, enumerate_paths


def describe_node(graph: ProcessGraph, node_id: str) -> str:
    node = graph.nodes[node_id]
    label = f' "{node.label}"' if node.label else ""
    return f"{node.id} [{node.kind}]{label}"


def describe_flow(path: ProcessPath, index: int) -> str:
    flow = path.flows[index]
    parts = [flow.id]
    if flow.name:
        parts.append(f'"{flow.name}"')
    if flow.condition is not None:
        parts.append(f"condition: {flow.condition}")
    return " | ".join(parts)


def format_result(graph: ProcessGraph, result: PathResult) -> str:
    lines = [
        f'Process "{graph.name}" (id={graph.id}): '
        f"{len(graph.nodes)} nodes, {len(graph.flows)} sequence flows",
        f"Found {len(result.paths)} path(s) from start to end "
        "(simple paths: no node is visited twice).",
    ]
    if result.loop_flows:
        lines.append(
            "Loop flows not re-traversed (would revisit a node): " + ", ".join(result.loop_flows)
        )
    for number, path in enumerate(result.paths, start=1):
        lines += ["", f"Path {number}:", f"  {describe_node(graph, path.nodes[0])}"]
        for i, node_id in enumerate(path.nodes[1:]):
            lines.append(f"    --({describe_flow(path, i)})-->")
            lines.append(f"  {describe_node(graph, node_id)}")
        conditions = path.conditions
        lines.append("  Conditions: " + (" AND ".join(conditions) if conditions else "(none)"))
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="bpmn-paths",
        description="Validate a BPMN file and print every start-to-end path.",
    )
    parser.add_argument("file", help="path to a .bpmn file")
    args = parser.parse_args(argv)

    try:
        graph = load_process(args.file)
    except BpmnError as exc:
        print(f"ERROR: {args.file}: {exc}", file=sys.stderr)
        return 1

    print(format_result(graph, enumerate_paths(graph)))
    return 0
