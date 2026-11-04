import sys
from collections.abc import Callable
from pathlib import Path

from bpmn_paths import enumerate_paths, load_process, parse_bpmn


def test_valid_file_has_two_simple_paths(valid_file: Path) -> None:
    result = enumerate_paths(load_process(valid_file))

    assert [p.nodes for p in result.paths] == [
        (
            "StartEvent_1",
            "assignApprover",
            "approveInvoice",
            "invoice_approved",
            "prepareBankTransfer",
            "ServiceTask_1",
            "invoiceProcessed",
        ),
        (
            "StartEvent_1",
            "assignApprover",
            "approveInvoice",
            "invoice_approved",
            "reviewInvoice",
            "reviewSuccessful_gw",
            "invoiceNotProcessed",
        ),
    ]


def test_path_conditions_follow_traversed_edges(valid_file: Path) -> None:
    approved, rejected = enumerate_paths(load_process(valid_file)).paths

    assert approved.conditions == ("${approved}",)
    assert rejected.conditions == ("${!approved}", "${!clarified}")
    assert [f.id for f in rejected.flows] == [
        "SequenceFlow_1",
        "sequenceFlow_178",
        "sequenceFlow_180",
        "invoiceNotApproved",
        "sequenceFlow_183",
        "reviewNotSuccessful",
    ]


def test_loop_is_detected_and_not_retraversed(valid_file: Path) -> None:
    result = enumerate_paths(load_process(valid_file))

    # reviewSuccessful leads back to approveInvoice, which is already on the path.
    assert result.loop_flows == ("reviewSuccessful",)
    for path in result.paths:
        assert len(path.nodes) == len(set(path.nodes))
        assert len(path.flows) == len(path.nodes) - 1


def test_branches_and_merge(write_bpmn: Callable[[str], Path]) -> None:
    path = write_bpmn("""
    <startEvent id="s"/>
    <exclusiveGateway id="g" gatewayDirection="Diverging"/>
    <task id="a"/>
    <task id="b"/>
    <task id="m"/>
    <endEvent id="e"/>
    <sequenceFlow id="f0" sourceRef="s" targetRef="g"/>
    <sequenceFlow id="fa" sourceRef="g" targetRef="a">
      <conditionExpression>${x}</conditionExpression>
    </sequenceFlow>
    <sequenceFlow id="fb" sourceRef="g" targetRef="b">
      <conditionExpression>${!x}</conditionExpression>
    </sequenceFlow>
    <sequenceFlow id="f1" sourceRef="a" targetRef="m"/>
    <sequenceFlow id="f2" sourceRef="b" targetRef="m"/>
    <sequenceFlow id="f3" sourceRef="m" targetRef="e"/>""")

    result = enumerate_paths(load_process(path))

    assert [p.nodes for p in result.paths] == [
        ("s", "g", "a", "m", "e"),
        ("s", "g", "b", "m", "e"),
    ]
    assert [p.conditions for p in result.paths] == [("${x}",), ("${!x}",)]
    assert result.loop_flows == ()


def test_self_loop_terminates(write_bpmn: Callable[[str], Path]) -> None:
    path = write_bpmn("""
    <startEvent id="s"/>
    <task id="t"/>
    <endEvent id="e"/>
    <sequenceFlow id="f0" sourceRef="s" targetRef="t"/>
    <sequenceFlow id="retry" sourceRef="t" targetRef="t"/>
    <sequenceFlow id="f1" sourceRef="t" targetRef="e"/>""")

    result = enumerate_paths(load_process(path))

    assert [p.nodes for p in result.paths] == [("s", "t", "e")]
    assert result.loop_flows == ("retry",)


def test_deep_graph_does_not_recurse(write_bpmn: Callable[[str], Path]) -> None:
    depth = sys.getrecursionlimit() * 3
    body = ['<startEvent id="n0"/>']
    body += [f'<task id="n{i}"/>' for i in range(1, depth)]
    body.append(f'<endEvent id="n{depth}"/>')
    body += [
        f'<sequenceFlow id="f{i}" sourceRef="n{i}" targetRef="n{i + 1}"/>' for i in range(depth)
    ]
    graph = parse_bpmn(write_bpmn("\n".join(body)))

    result = enumerate_paths(graph)

    assert len(result.paths) == 1
    assert len(result.paths[0].nodes) == depth + 1
