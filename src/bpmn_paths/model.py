"""Graph data model and error types."""

from collections import defaultdict
from dataclasses import dataclass
from functools import cached_property


@dataclass(frozen=True)
class Node:
    """A BPMN flow node (event, task, gateway, ...)."""

    id: str
    kind: str  # local XML tag name, e.g. "startEvent", "userTask", "exclusiveGateway"
    name: str = ""
    gateway_direction: str = ""
    # <incoming>/<outgoing> flow IDs as declared inside the node element.
    declared_incoming: tuple[str, ...] = ()
    declared_outgoing: tuple[str, ...] = ()

    @property
    def label(self) -> str:
        """Name with line breaks collapsed, for display only."""
        return " ".join(self.name.split())


@dataclass(frozen=True)
class Flow:
    """A BPMN sequence flow (directed edge). ``condition`` is the raw text from the file."""

    id: str
    source: str
    target: str
    name: str = ""
    condition: str | None = None


@dataclass(frozen=True)
class ProcessGraph:
    """Nodes and sequence flows of one BPMN process, in document order.

    Flows are kept even if they reference unknown nodes, so validation can report them.
    """

    id: str
    name: str
    nodes: dict[str, Node]
    flows: dict[str, Flow]
    duplicate_ids: tuple[str, ...] = ()

    @cached_property
    def _outgoing(self) -> dict[str, list[Flow]]:
        index: dict[str, list[Flow]] = defaultdict(list)
        for flow in self.flows.values():
            index[flow.source].append(flow)
        return index

    @cached_property
    def _incoming(self) -> dict[str, list[Flow]]:
        index: dict[str, list[Flow]] = defaultdict(list)
        for flow in self.flows.values():
            index[flow.target].append(flow)
        return index

    def outgoing(self, node_id: str) -> list[Flow]:
        return self._outgoing.get(node_id, [])

    def incoming(self, node_id: str) -> list[Flow]:
        return self._incoming.get(node_id, [])

    def nodes_of_kind(self, kind: str) -> list[Node]:
        return [n for n in self.nodes.values() if n.kind == kind]


@dataclass(frozen=True)
class Issue:
    """One validation problem, tied to the ID of the faulty element."""

    element_id: str
    message: str

    def __str__(self) -> str:
        return f"[{self.element_id}] {self.message}"


class BpmnError(Exception):
    """Base class for all errors raised by this package."""


class BpmnParseError(BpmnError):
    """The file cannot be read or is not a usable BPMN document."""


class BpmnValidationError(BpmnError):
    """The BPMN document was parsed but its graph is structurally invalid."""

    def __init__(self, issues: list[Issue]) -> None:
        self.issues = issues
        lines = [f"invalid BPMN process ({len(issues)} problem(s)):"]
        lines += [f"  - {issue}" for issue in issues]
        super().__init__("\n".join(lines))

    @property
    def element_ids(self) -> list[str]:
        """Faulty element IDs, unique, in report order."""
        return list(dict.fromkeys(issue.element_id for issue in self.issues))
