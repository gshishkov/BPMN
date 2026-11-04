from collections.abc import Callable
from pathlib import Path

import pytest

from bpmn_paths import BpmnValidationError, find_issues, load_process, parse_bpmn


def issue_messages(path: Path, element_id: str) -> list[str]:
    return [i.message for i in find_issues(parse_bpmn(path)) if i.element_id == element_id]


def test_valid_file_has_no_issues(valid_file: Path) -> None:
    assert find_issues(parse_bpmn(valid_file)) == []


def test_broken_file_is_rejected(broken_file: Path) -> None:
    with pytest.raises(BpmnValidationError) as exc_info:
        load_process(broken_file)

    error = exc_info.value
    assert "SequenceFlow_2" in str(error)
    assert "invoiceNotProcessed" in str(error)
    assert {"SequenceFlow_2", "invoiceNotProcessed", "reviewSuccessful_gw"} <= set(
        error.element_ids
    )


# Defect 1: SequenceFlow_2 points to a node that does not exist.
def test_defect_dangling_target_ref(broken_file: Path) -> None:
    assert issue_messages(broken_file, "SequenceFlow_2") == [
        "sequenceFlow targetRef='ServiceTask_9' does not reference an existing flow node"
    ]


def test_defect_dangling_target_side_effects(broken_file: Path) -> None:
    # ServiceTask_1 still declares SequenceFlow_2 as incoming, but nothing reaches it now.
    messages = issue_messages(broken_file, "ServiceTask_1")
    assert (
        "declares <incoming>SequenceFlow_2</incoming>, but that flow targets 'ServiceTask_9'"
        in (messages)
    )
    assert "serviceTask has no incoming sequence flow" in messages


# Defect 2: flow reviewNotSuccessful was removed -> end event orphaned, gateway has one exit.
def test_defect_missing_flow_orphans_end_event(broken_file: Path) -> None:
    assert issue_messages(broken_file, "invoiceNotProcessed") == [
        "endEvent has no incoming sequence flow"
    ]


def test_defect_missing_flow_leaves_gateway_single_exit(broken_file: Path) -> None:
    assert issue_messages(broken_file, "reviewSuccessful_gw") == [
        "diverging exclusiveGateway has 1 outgoing sequence flow(s), expected at least 2"
    ]


def test_broken_file_reports_root_causes_only(broken_file: Path) -> None:
    # Follow-up reachability errors are suppressed while structural errors exist.
    issues = find_issues(parse_bpmn(broken_file))
    assert len(issues) == 5
    assert {i.element_id for i in issues} == {
        "SequenceFlow_2",
        "ServiceTask_1",
        "invoiceNotProcessed",
        "reviewSuccessful_gw",
    }


def test_unknown_source_ref(write_bpmn: Callable[[str], Path]) -> None:
    path = write_bpmn("""
    <startEvent id="s"/>
    <endEvent id="e"/>
    <sequenceFlow id="f1" sourceRef="s" targetRef="e"/>
    <sequenceFlow id="f2" sourceRef="ghost" targetRef="e"/>""")

    assert issue_messages(path, "f2") == [
        "sequenceFlow sourceRef='ghost' does not reference an existing flow node"
    ]


def test_duplicate_id(write_bpmn: Callable[[str], Path]) -> None:
    path = write_bpmn("""
    <startEvent id="s"/>
    <endEvent id="e"/>
    <sequenceFlow id="s" sourceRef="s" targetRef="e"/>""")

    assert "ID is used by more than one element" in issue_messages(path, "s")


def test_missing_start_event(write_bpmn: Callable[[str], Path]) -> None:
    path = write_bpmn("""
    <task id="t"/>
    <endEvent id="e"/>
    <sequenceFlow id="f" sourceRef="t" targetRef="e"/>""")

    assert "process has no startEvent" in issue_messages(path, "p")


def test_cycle_without_exit_is_rejected(write_bpmn: Callable[[str], Path]) -> None:
    # s -> a <-> b: every node is locally connected, but the loop never reaches e.
    path = write_bpmn("""
    <startEvent id="s"/>
    <task id="a"/>
    <task id="b"/>
    <task id="c"/>
    <endEvent id="e"/>
    <sequenceFlow id="f0" sourceRef="s" targetRef="a"/>
    <sequenceFlow id="f1" sourceRef="a" targetRef="b"/>
    <sequenceFlow id="f2" sourceRef="b" targetRef="a"/>
    <sequenceFlow id="f3" sourceRef="c" targetRef="e"/>
    <sequenceFlow id="f4" sourceRef="c" targetRef="c"/>""")

    issues = find_issues(parse_bpmn(path))
    assert {str(i) for i in issues} == {
        "[c] task is not reachable from any startEvent",
        "[e] endEvent is not reachable from any startEvent",
        "[s] startEvent cannot reach any endEvent",
        "[a] task cannot reach any endEvent",
        "[b] task cannot reach any endEvent",
    }
