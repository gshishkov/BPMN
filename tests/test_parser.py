from collections.abc import Callable
from pathlib import Path

import pytest

from bpmn_paths import BpmnParseError, load_process, parse_bpmn


def test_valid_file_parses_and_validates(valid_file: Path) -> None:
    graph = load_process(valid_file)

    assert graph.id == "invoice"
    assert graph.name == "Invoice Receipt"
    assert set(graph.nodes) == {
        "StartEvent_1",
        "assignApprover",
        "approveInvoice",
        "invoice_approved",
        "reviewInvoice",
        "reviewSuccessful_gw",
        "prepareBankTransfer",
        "ServiceTask_1",
        "invoiceProcessed",
        "invoiceNotProcessed",
    }
    assert len(graph.flows) == 10
    assert graph.nodes["StartEvent_1"].kind == "startEvent"
    assert graph.nodes["reviewInvoice"].kind == "callActivity"
    assert graph.nodes["invoice_approved"].kind == "exclusiveGateway"


def test_non_flow_elements_are_not_nodes(valid_file: Path) -> None:
    graph = parse_bpmn(valid_file)

    for element_id in ("laneSet_5", "DataStoreReference_1", "Accountant"):
        assert element_id not in graph.nodes


def test_edges_connect_expected_nodes(valid_file: Path) -> None:
    graph = parse_bpmn(valid_file)

    flow = graph.flows["invoiceNotApproved"]
    assert (flow.source, flow.target) == ("invoice_approved", "reviewInvoice")
    assert [f.id for f in graph.outgoing("invoice_approved")] == [
        "invoiceApproved",
        "invoiceNotApproved",
    ]
    assert {f.id for f in graph.incoming("approveInvoice")} == {
        "sequenceFlow_178",
        "reviewSuccessful",
    }


def test_conditions_preserved_verbatim(valid_file: Path) -> None:
    flows = parse_bpmn(valid_file).flows

    assert flows["reviewSuccessful"].condition == "${clarified}"
    assert flows["reviewNotSuccessful"].condition == "${!clarified}"
    assert flows["invoiceApproved"].condition == "${approved}"
    assert flows["invoiceNotApproved"].condition == "${!approved}"
    assert flows["invoiceApproved"].name == "yes"
    assert flows["invoiceNotApproved"].name == "no"


def test_flows_without_condition_have_none(valid_file: Path) -> None:
    flows = parse_bpmn(valid_file).flows

    unconditional = {fid for fid, f in flows.items() if f.condition is None}
    assert unconditional == {
        "SequenceFlow_1",
        "SequenceFlow_2",
        "SequenceFlow_3",
        "sequenceFlow_178",
        "sequenceFlow_180",
        "sequenceFlow_183",
    }


def test_condition_whitespace_and_symbols_not_altered(
    write_bpmn: Callable[[str], Path],
) -> None:
    raw = "  ${amount > 1000 &amp;&amp; category == 'travel'}  "
    path = write_bpmn(f"""
    <startEvent id="s"/>
    <endEvent id="e"/>
    <sequenceFlow id="f" sourceRef="s" targetRef="e">
      <conditionExpression>{raw}</conditionExpression>
    </sequenceFlow>""")

    assert parse_bpmn(path).flows["f"].condition == "  ${amount > 1000 && category == 'travel'}  "


def test_missing_file_raises_parse_error(tmp_path: Path) -> None:
    with pytest.raises(BpmnParseError, match="file not found"):
        parse_bpmn(tmp_path / "nope.bpmn")


def test_malformed_xml_raises_parse_error(tmp_path: Path) -> None:
    path = tmp_path / "bad.bpmn"
    path.write_text("<definitions><process>", encoding="utf-8")

    with pytest.raises(BpmnParseError, match="malformed XML"):
        parse_bpmn(path)


def test_non_bpmn_root_raises_parse_error(tmp_path: Path) -> None:
    path = tmp_path / "other.xml"
    path.write_text("<root/>", encoding="utf-8")

    with pytest.raises(BpmnParseError, match="not BPMN"):
        parse_bpmn(path)
