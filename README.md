# bpmn-paths

Parses a BPMN 2.0 file into a graph, validates it, and prints every path from a start
event to an end event, with the condition of each traversed sequence flow kept exactly as written.

The runtime uses only the standard library (`xml.etree.ElementTree`).

## Usage

```bash
uv sync
uv run python -m bpmn_paths src/data/invoice.bpmn
uv run python -m bpmn_paths src/data/invoice-broken.bpmn   # exit code 1, lists faulty element IDs
uv run pytest
```

## Design

| Module | Responsibility |
|---|---|
| `model.py` | `Node`, `Flow`, `ProcessGraph` dataclasses; `Issue` and error types |
| `parser.py` | XML → `ProcessGraph` (flow nodes and sequence flows of the single `<process>`) |
| `validation.py` | Structural checks; raises `BpmnValidationError` with one `Issue` per faulty element ID |
| `paths.py` | Iterative DFS path enumeration |
| `cli.py` | argparse entry point and output formatting |

**What "every path" means:** every *simple* path from a start event to an end event,
where no node appears twice. A flow that would go back to a node already on the current
path (a loop) is not followed again; it is reported as a loop flow instead. This keeps
the result finite. The search uses an explicit stack, not recursion.

**Validation:** these checks run first:
- duplicate or missing IDs
- `sourceRef`/`targetRef` pointing to unknown nodes
- `<incoming>`/`<outgoing>` declarations that don't match the flows
- missing start or end events, and nodes without incoming or outgoing flows
- diverging gateways with fewer than 2 exits

Reachability (every node reachable from a start event and able to reach an end event)
is checked only if those checks pass. Otherwise one broken reference would bury the root
cause under follow-up errors.
