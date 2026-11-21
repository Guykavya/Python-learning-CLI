## Approach

The model answer is in `answer.md`. One table helps to remember the six cases:

| Line | Problem | The rule it breaks |
|---|---|---|
| (a) | password and e-mail in the log, `print` | no secrets, no personal data; use the logger |
| (b) | whole request body | log what you need, not everything |
| (c) | facts inside the message | constant `msg`, facts as fields |
| (d) | traceback in many records | one event, one record |
| (e) | `print` at start-up | levels, timestamps, request id, JSON |
| (f) | failure at INFO | levels with meaning |

## Cost

Nothing to build. The cost of getting it wrong shows later: a leaked password in a log vendor, an alert that never fires because errors are logged at INFO, a `jq` query that cannot find "order created" because every message differs.

## Another way

Write the rules as a code review checklist and as a test: a unit test that logs one event and asserts that the output is one JSON line with the fixed keys (problem p013), and a grep in CI for `print(` in application code.
