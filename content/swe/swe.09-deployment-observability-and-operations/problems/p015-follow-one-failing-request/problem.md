# Follow one failing request

Chapter sections 8.3 (`jq`, the tool for reading JSON logs), 8.4 (tutorial: trace one failing request) and 8.5 (across services, workers and machines). This is the first outcome of the module: **trace one failing request through the logs using its request id.** A customer gives you an error id. The logs of the web app and of the background worker are mixed in one stream, together with noise. Write what the `jq` commands of the tutorial do, as a function you can test.

## What to write

```python
def trace_request(lines: list[str], request_id: str) -> dict: ...
```

`lines` are lines of a combined log. Each valid line is a JSON object like

```json
{"ts":"2026-11-09T07:13:20.115Z","service":"web","level":"INFO","logger":"pagebound","msg":"request finished","request_id":"8fad38b4","status":500}
```

Rules:

- Lines that are blank, **not JSON**, not a JSON object, or have a different `request_id` (exact comparison; `abc` is not `ABC`) are ignored.
- The matching lines are the **events** of the request. Each event is a dict with exactly the keys `ts`, `service`, `level`, `msg`, taken from the line. A missing `service` becomes `"unknown"`; a missing `ts`, `level` or `msg` becomes `""`.
- The events are sorted by `ts` (ISO 8601 strings, so string order is time order; the sort is stable, so events with the same `ts` stay in input order; a missing `ts` sorts first).
- Return a dict with three keys:

| Key | Value |
|---|---|
| `events` | the sorted list of events |
| `first_error` | the first event (in the sorted list) whose `level` is `"ERROR"` or `"CRITICAL"`, or `None` |
| `services` | the names of the services the request passed through, **in order of their first event** (no duplicates) |

## Example

```python
lines = [
    '{"ts":"2026-11-09T07:00:02.000Z","service":"worker","level":"ERROR","msg":"report failed","request_id":"8fad38b4"}',
    "docker: a line that is not JSON",
    '{"ts":"2026-11-09T07:00:01.000Z","service":"web","level":"INFO","msg":"request finished","request_id":"8fad38b4"}',
    '{"ts":"2026-11-09T07:00:01.500Z","service":"web","level":"INFO","msg":"request finished","request_id":"someone-else"}',
]
trace_request(lines, "8fad38b4")
# {'events': [{'ts': '2026-11-09T07:00:01.000Z', 'service': 'web', 'level': 'INFO', 'msg': 'request finished'},
#             {'ts': '2026-11-09T07:00:02.000Z', 'service': 'worker', 'level': 'ERROR', 'msg': 'report failed'}],
#  'first_error': {'ts': '2026-11-09T07:00:02.000Z', 'service': 'worker', 'level': 'ERROR', 'msg': 'report failed'},
#  'services': ['web', 'worker']}
```

In the shell the same question is `jq -c --arg id "$ID" 'select(.request_id == $id)' app.log`. The function is what you keep when you want a test, a report or an alert that says where the request went wrong.
