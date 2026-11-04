"""Read a BPMN 2.0 XML file into a :class:`ProcessGraph` using xml.etree.ElementTree."""

import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

from bpmn_paths.model import BpmnParseError, Flow, Node, ProcessGraph
from bpmn_paths.validation import validate

BPMN_NS = "http://www.omg.org/spec/BPMN/20100524/MODEL"
NS = {"bpmn": BPMN_NS}

# Elements that take part in the sequence-flow graph.
FLOW_NODE_TAGS = frozenset(
    {
        "startEvent",
        "endEvent",
        "intermediateCatchEvent",
        "intermediateThrowEvent",
        "boundaryEvent",
        "task",
        "userTask",
        "serviceTask",
        "scriptTask",
        "businessRuleTask",
        "sendTask",
        "receiveTask",
        "manualTask",
        "callActivity",
        "subProcess",
        "exclusiveGateway",
        "inclusiveGateway",
        "parallelGateway",
        "eventBasedGateway",
        "complexGateway",
    }
)


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _refs(element: ET.Element, tag: str) -> tuple[str, ...]:
    return tuple((e.text or "").strip() for e in element.findall(f"bpmn:{tag}", NS))


def _parse_node(element: ET.Element) -> Node:
    return Node(
        id=element.get("id", ""),
        kind=_local(element.tag),
        name=element.get("name", ""),
        gateway_direction=element.get("gatewayDirection", ""),
        declared_incoming=_refs(element, "incoming"),
        declared_outgoing=_refs(element, "outgoing"),
    )


def _parse_flow(element: ET.Element) -> Flow:
    condition_el = element.find("bpmn:conditionExpression", NS)
    return Flow(
        id=element.get("id", ""),
        source=element.get("sourceRef", ""),
        target=element.get("targetRef", ""),
        name=element.get("name", ""),
        # Kept verbatim: no stripping, no evaluation.
        condition=None if condition_el is None else (condition_el.text or ""),
    )


def parse_process(process: ET.Element) -> ProcessGraph:
    nodes: dict[str, Node] = {}
    flows: dict[str, Flow] = {}
    ids: list[str] = []
    for child in process:
        tag = _local(child.tag)
        if tag == "sequenceFlow":
            flow = _parse_flow(child)
            flows.setdefault(flow.id, flow)
            ids.append(flow.id)
        elif tag in FLOW_NODE_TAGS:
            node = _parse_node(child)
            nodes.setdefault(node.id, node)
            ids.append(node.id)
    duplicates = tuple(i for i, count in Counter(ids).items() if count > 1)
    return ProcessGraph(
        id=process.get("id", ""),
        name=process.get("name", ""),
        nodes=nodes,
        flows=flows,
        duplicate_ids=duplicates,
    )


def parse_bpmn(path: str | Path) -> ProcessGraph:
    """Parse the single ``<process>`` of a BPMN file. Does not validate the graph."""
    try:
        root = ET.parse(path).getroot()
    except FileNotFoundError as exc:
        raise BpmnParseError(f"file not found: {path}") from exc
    except ET.ParseError as exc:
        raise BpmnParseError(f"malformed XML in {path}: {exc}") from exc

    if root.tag != f"{{{BPMN_NS}}}definitions":
        raise BpmnParseError(f"{path}: root element is not BPMN <definitions>")
    processes = root.findall("bpmn:process", NS)
    if len(processes) != 1:
        raise BpmnParseError(f"{path}: expected exactly 1 <process>, found {len(processes)}")
    return parse_process(processes[0])


def load_process(path: str | Path) -> ProcessGraph:
    """Parse and validate; raises BpmnValidationError listing every faulty element ID."""
    graph = parse_bpmn(path)
    validate(graph)
    return graph
