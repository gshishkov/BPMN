from pathlib import Path

import pytest

from bpmn_paths.cli import main


def test_cli_prints_paths_for_valid_file(
    valid_file: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main([str(valid_file)]) == 0

    out = capsys.readouterr().out
    assert "Found 2 path(s)" in out
    assert "Path 1:" in out
    assert "Path 2:" in out
    assert '--(invoiceApproved | "yes" | condition: ${approved})-->' in out
    assert "Conditions: ${!approved} AND ${!clarified}" in out
    assert "Loop flows not re-traversed (would revisit a node): reviewSuccessful" in out


def test_cli_rejects_broken_file(broken_file: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main([str(broken_file)]) == 1

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "ERROR:" in captured.err
    assert "[SequenceFlow_2] sequenceFlow targetRef='ServiceTask_9'" in captured.err
    assert "[invoiceNotProcessed] endEvent has no incoming sequence flow" in captured.err


def test_cli_missing_file(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main([str(tmp_path / "missing.bpmn")]) == 1
    assert "file not found" in capsys.readouterr().err
