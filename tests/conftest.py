from collections.abc import Callable
from pathlib import Path

import pytest

DATA_DIR = Path(__file__).resolve().parents[1] / "src" / "data"

BPMN_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://www.omg.org/spec/BPMN/20100524/MODEL" id="defs">
  <process id="p" name="Test">
{body}
  </process>
</definitions>
"""


@pytest.fixture
def valid_file() -> Path:
    return DATA_DIR / "invoice.bpmn"


@pytest.fixture
def broken_file() -> Path:
    return DATA_DIR / "invoice-broken.bpmn"


@pytest.fixture
def write_bpmn(tmp_path: Path) -> Callable[[str], Path]:
    """Write a minimal BPMN document whose <process> contains ``body``."""

    def write(body: str) -> Path:
        path = tmp_path / "test.bpmn"
        path.write_text(BPMN_TEMPLATE.format(body=body), encoding="utf-8")
        return path

    return write
