# Final result — BPMN path enumeration

The code parses a BPMN 2.0 file into a graph, validates it, and prints every start-to-end path with the conditions of the flows it passes through. Only the standard library is used (`xml.etree.ElementTree`).

**Tests:** `uv run pytest` → 29 passed (latest run, Python 3.12.16). `ruff` and `mypy --strict` report no problems.

## Implementation summary

The code lives in `src/bpmn_paths/`:

| Module | Responsibility |
|---|---|
| [model.py](src/bpmn_paths/model.py) | `Node`, `Flow`, `ProcessGraph` dataclasses, `Issue`, and the error types |
| [parser.py](src/bpmn_paths/parser.py) | Reads the XML into a graph of nodes (events, tasks, gateways) and edges (sequence flows). Conditions are stored exactly as written. Lanes and data stores are ignored. |
| [validation.py](src/bpmn_paths/validation.py) | Collects every problem rather than stopping at the first. Each problem names the faulty element ID. |
| [paths.py](src/bpmn_paths/paths.py) | Enumerates paths with an explicit stack instead of recursion |
| [cli.py](src/bpmn_paths/cli.py) | Command line interface. Exit code 0 = valid, 1 = invalid or unreadable file. |

Validation checks:
- duplicate or missing IDs
- `sourceRef`/`targetRef` pointing to elements that don't exist
- `<incoming>`/`<outgoing>` declarations that don't match the flows
- missing start or end events
- nodes with no incoming or outgoing flow
- decision gateways with fewer than 2 exits

Reachability (every node can be reached from the start and can reach an end) is checked only after those pass. Otherwise one broken reference would bury the real cause under follow-up errors.

**What "every path" means:** every *simple* path from a start event to an end event, where no node is visited twice. A flow that would return to a node already on the current path is not followed again; it is listed as a loop flow instead. This keeps the result finite even though the model has a loop. A test runs the enumeration on a chain three times longer than Python's recursion limit.

The 29 tests in `tests/` cover:
- parsing the valid file
- conditions preserved verbatim
- path enumeration, including loops, a self-loop and the no-recursion case
- rejection of the broken file and each of its defects
- CLI output and exit codes

## Defects found in invoice-broken.bpmn

1. **`SequenceFlow_2` points to an element that doesn't exist.** Its `targetRef` is `ServiceTask_9` (in the valid file it is `ServiceTask_1`). As a result, `ServiceTask_1` still declares `<incoming>SequenceFlow_2</incoming>` but no flow actually arrives at it.
2. **Flow `reviewNotSuccessful` has been deleted,** together with its `<incoming>`/`<outgoing>` references. It ran from `reviewSuccessful_gw` to `invoiceNotProcessed` with condition `${!clarified}`. Without it:
   - end event `invoiceNotProcessed` has no incoming flow, so it can never be reached;
   - decision gateway `reviewSuccessful_gw` has only one exit.

## Paths in the valid file: 2

The loop `approveInvoice → invoice_approved → reviewInvoice → reviewSuccessful_gw → approveInvoice` is followed once per path. Its closing flow `reviewSuccessful` is not taken again.

| # | Ends at | Conditions |
|---|---|---|
| 1 | `invoiceProcessed` | `${approved}` |
| 2 | `invoiceNotProcessed` | `${!approved}` AND `${!clarified}` |

```text
$ uv run python -m bpmn_paths src/data/invoice.bpmn
Process "Invoice Receipt" (id=invoice): 10 nodes, 10 sequence flows
Found 2 path(s) from start to end (simple paths: no node is visited twice).
Loop flows not re-traversed (would revisit a node): reviewSuccessful

Path 1:
  StartEvent_1 [startEvent] "Invoice received"
    --(SequenceFlow_1)-->
  assignApprover [businessRuleTask] "Assign Approver Group"
    --(sequenceFlow_178)-->
  approveInvoice [userTask] "Approve Invoice"
    --(sequenceFlow_180)-->
  invoice_approved [exclusiveGateway] "Invoice approved?"
    --(invoiceApproved | "yes" | condition: ${approved})-->
  prepareBankTransfer [userTask] "Prepare Bank Transfer"
    --(SequenceFlow_2)-->
  ServiceTask_1 [serviceTask] "Archive Invoice"
    --(SequenceFlow_3)-->
  invoiceProcessed [endEvent] "Invoice processed"
  Conditions: ${approved}

Path 2:
  StartEvent_1 [startEvent] "Invoice received"
    --(SequenceFlow_1)-->
  assignApprover [businessRuleTask] "Assign Approver Group"
    --(sequenceFlow_178)-->
  approveInvoice [userTask] "Approve Invoice"
    --(sequenceFlow_180)-->
  invoice_approved [exclusiveGateway] "Invoice approved?"
    --(invoiceNotApproved | "no" | condition: ${!approved})-->
  reviewInvoice [callActivity] "Review Invoice"
    --(sequenceFlow_183)-->
  reviewSuccessful_gw [exclusiveGateway] "Review successful?"
    --(reviewNotSuccessful | "no" | condition: ${!clarified})-->
  invoiceNotProcessed [endEvent] "Invoice not processed"
  Conditions: ${!approved} AND ${!clarified}
```

## Broken file example

```text
$ uv run python -m bpmn_paths src/data/invoice-broken.bpmn
ERROR: src/data/invoice-broken.bpmn: invalid BPMN process (5 problem(s)):
  - [SequenceFlow_2] sequenceFlow targetRef='ServiceTask_9' does not reference an existing flow node
  - [ServiceTask_1] declares <incoming>SequenceFlow_2</incoming>, but that flow targets 'ServiceTask_9'
  - [reviewSuccessful_gw] diverging exclusiveGateway has 1 outgoing sequence flow(s), expected at least 2
  - [invoiceNotProcessed] endEvent has no incoming sequence flow
  - [ServiceTask_1] serviceTask has no incoming sequence flow
```

The exit code is 1.

## Commands

```bash
uv sync
uv run python -m bpmn_paths src/data/invoice.bpmn
uv run python -m bpmn_paths src/data/invoice-broken.bpmn
uv run pytest -v
uv run ruff check . && uv run mypy src tests
```
