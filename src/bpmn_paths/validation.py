"""Structural validation of a parsed BPMN graph."""

from collections.abc import Callable, Iterable

from bpmn_paths.model import BpmnValidationError, Issue, ProcessGraph


def check_ids(graph: ProcessGraph) -> Iterable[Issue]:
    for element_id in graph.duplicate_ids:
        yield Issue(element_id, "ID is used by more than one element")
    for node in graph.nodes.values():
        if not node.id:
            yield Issue("<missing id>", f"{node.kind} element has no id attribute")
    for flow in graph.flows.values():
        if not flow.id:
            yield Issue("<missing id>", "sequenceFlow element has no id attribute")


def check_flow_references(graph: ProcessGraph) -> Iterable[Issue]:
    """Every sequence flow must connect two existing flow nodes."""
    for flow in graph.flows.values():
        for attr, ref in (("sourceRef", flow.source), ("targetRef", flow.target)):
            if not ref:
                yield Issue(flow.id, f"sequenceFlow has no {attr}")
            elif ref not in graph.nodes:
                yield Issue(
                    flow.id,
                    f"sequenceFlow {attr}='{ref}' does not reference an existing flow node",
                )


def check_declared_refs(graph: ProcessGraph) -> Iterable[Issue]:
    """<incoming>/<outgoing> inside a node must match the sequence flows' source/target."""
    for node in graph.nodes.values():
        for ref in node.declared_incoming:
            flow = graph.flows.get(ref)
            if flow is None:
                yield Issue(node.id, f"declares <incoming>{ref}</incoming>, no such sequenceFlow")
            elif flow.target != node.id:
                yield Issue(
                    node.id,
                    f"declares <incoming>{ref}</incoming>, but that flow targets '{flow.target}'",
                )
        for ref in node.declared_outgoing:
            flow = graph.flows.get(ref)
            if flow is None:
                yield Issue(node.id, f"declares <outgoing>{ref}</outgoing>, no such sequenceFlow")
            elif flow.source != node.id:
                yield Issue(
                    node.id,
                    f"declares <outgoing>{ref}</outgoing>, but that flow starts at '{flow.source}'",
                )


def check_connectivity(graph: ProcessGraph) -> Iterable[Issue]:
    """Start/end events, dangling nodes and diverging gateways."""
    if not graph.nodes_of_kind("startEvent"):
        yield Issue(graph.id, "process has no startEvent")
    if not graph.nodes_of_kind("endEvent"):
        yield Issue(graph.id, "process has no endEvent")

    for node in graph.nodes.values():
        n_in = len(graph.incoming(node.id))
        n_out = len(graph.outgoing(node.id))
        if node.kind == "startEvent":
            if n_in:
                yield Issue(node.id, "startEvent must not have incoming sequence flows")
        elif n_in == 0:
            yield Issue(node.id, f"{node.kind} has no incoming sequence flow")
        if node.kind == "endEvent":
            if n_out:
                yield Issue(node.id, "endEvent must not have outgoing sequence flows")
        elif n_out == 0:
            yield Issue(node.id, f"{node.kind} has no outgoing sequence flow")
        if node.gateway_direction == "Diverging" and n_out < 2:
            yield Issue(
                node.id,
                f"diverging {node.kind} has {n_out} outgoing sequence flow(s), expected at least 2",
            )


def _reachable(start: Iterable[str], step: Callable[[str], Iterable[str]]) -> set[str]:
    """Iterative graph search (no recursion)."""
    seen = set(start)
    stack = list(seen)
    while stack:
        for nxt in step(stack.pop()):
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    return seen


def check_reachability(graph: ProcessGraph) -> Iterable[Issue]:
    """Every node must be reachable from a start event and must lead to an end event."""
    known = graph.nodes.keys()
    from_start = _reachable(
        (n.id for n in graph.nodes_of_kind("startEvent")),
        lambda nid: (f.target for f in graph.outgoing(nid) if f.target in known),
    )
    to_end = _reachable(
        (n.id for n in graph.nodes_of_kind("endEvent")),
        lambda nid: (f.source for f in graph.incoming(nid) if f.source in known),
    )
    for node in graph.nodes.values():
        if node.id not in from_start:
            yield Issue(node.id, f"{node.kind} is not reachable from any startEvent")
        if node.id not in to_end:
            yield Issue(node.id, f"{node.kind} cannot reach any endEvent")


LOCAL_CHECKS = (
    check_ids,
    check_flow_references,
    check_declared_refs,
    check_connectivity,
)


def find_issues(graph: ProcessGraph) -> list[Issue]:
    """Local checks first; reachability only if they pass.

    A broken reference makes most of the graph unreachable, so reporting reachability
    afterwards would bury the root cause under follow-up errors.
    """
    issues = [issue for check in LOCAL_CHECKS for issue in check(graph)]
    return issues or list(check_reachability(graph))


def validate(graph: ProcessGraph) -> None:
    """Raise BpmnValidationError with all issues found, or return if the graph is valid."""
    issues = find_issues(graph)
    if issues:
        raise BpmnValidationError(issues)
