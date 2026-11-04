"""Enumerate start-to-end paths of a validated graph.

Definition of "every path": every *simple* path from a startEvent to an endEvent, i.e. a
path on which no node appears twice. A loop is therefore traversed at most once per path;
a flow that would return to a node already on the path is not followed (it is recorded
as a loop flow instead). This keeps the result finite on cyclic graphs.

The search is an iterative depth-first search with an explicit stack: no recursion, so
deep graphs cannot hit Python's recursion limit.
"""

from dataclasses import dataclass

from bpmn_paths.model import Flow, ProcessGraph


@dataclass(frozen=True)
class ProcessPath:
    """Nodes visited in order; ``flows[i]`` connects ``nodes[i]`` to ``nodes[i + 1]``."""

    nodes: tuple[str, ...]
    flows: tuple[Flow, ...]

    @property
    def conditions(self) -> tuple[str, ...]:
        return tuple(f.condition for f in self.flows if f.condition is not None)


@dataclass(frozen=True)
class PathResult:
    paths: tuple[ProcessPath, ...]
    loop_flows: tuple[str, ...]  # flows skipped because they close a cycle


def enumerate_paths(graph: ProcessGraph) -> PathResult:
    end_ids = {n.id for n in graph.nodes_of_kind("endEvent")}
    paths: list[ProcessPath] = []
    loop_flows: dict[str, None] = {}  # ordered set

    for start in graph.nodes_of_kind("startEvent"):
        stack: list[ProcessPath] = [ProcessPath((start.id,), ())]
        while stack:
            path = stack.pop()
            current = path.nodes[-1]
            if current in end_ids:
                paths.append(path)
                continue
            # Reversed so that flows are explored in document order.
            for flow in reversed(graph.outgoing(current)):
                if flow.target in path.nodes:
                    loop_flows[flow.id] = None
                elif flow.target in graph.nodes:
                    stack.append(ProcessPath((*path.nodes, flow.target), (*path.flows, flow)))

    return PathResult(tuple(paths), tuple(loop_flows))
