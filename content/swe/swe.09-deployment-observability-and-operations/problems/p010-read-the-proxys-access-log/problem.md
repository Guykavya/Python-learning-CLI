# Read the proxy's access log

Chapter sections 7.2 (the JSON access log), 7.4 (502 and 504) and "Try it: read the log". Nginx writes one JSON object per request (the chapter's `log_format json_log`):

```json
{"ts":"2026-11-09T07:13:20+00:00","remote":"172.19.0.1","method":"GET","uri":"/orders/1","status":404,"bytes":28,"duration":0.003,"upstream":"172.19.0.3:8000","upstream_status":"404","request_id":"2bd7f8f0a1ca53e9fbc29657746c07fa"}
```

`status` is a number, `duration` is the request time in seconds, and `upstream_status` is a **string**: the status of each backend that Nginx tried, separated by `, ` (`"504, 504, 504"` means three tries), or `"-"` when no backend answered at all (the connection failed). Write two functions that turn such a log into answers.

## What to write

```python
def parse_access_line(line: str) -> dict: ...
def summarise(lines: list[str]) -> dict: ...
```

**`parse_access_line(line)`** returns a dict with exactly these keys: `request_id`, `method`, `uri`, `status` (int), `duration` (float), `upstream_status` (str; `"-"` if the field is missing) and `upstream_tries` (int: `0` when `upstream_status` is `"-"` or empty, otherwise the number of comma-separated parts). It raises `ValueError` if the line is not a JSON object or lacks any of `request_id`, `method`, `uri`, `status`, `duration`.

**`summarise(lines)`** reads many lines, **skipping and counting** the ones that are blank or are not valid access lines (a container's log also holds other text). It returns a dict with:

| Key | Value |
|---|---|
| `requests` | the number of valid access lines |
| `skipped` | the number of non-blank lines that were not valid (blank lines are not counted at all) |
| `by_status` | `{status: count}` |
| `slowest` | the 3 slowest requests as `{"request_id", "uri", "duration"}` dicts, slowest first (ties: smaller `request_id` first); fewer than 3 if there are fewer requests |
| `share_5xx` | the share of requests with a status from 500 to 599, a float from 0 to 1 (`0.0` when there are no requests) |

## Example

```python
line = '{"method":"GET","uri":"/boom","status":504,"duration":15.011,"upstream_status":"504, 504, 504","request_id":"abc12345"}'
parse_access_line(line)
# {'request_id': 'abc12345', 'method': 'GET', 'uri': '/boom', 'status': 504, 'duration': 15.011,
#  'upstream_status': '504, 504, 504', 'upstream_tries': 3}
```

An answer to the chapter's "Try it": `"status":502` with `"upstream_status":"-"` means `upstream_tries == 0`: Nginx never got an answer from any backend.
