## Hint 1

`parse_access_line` is the careful part: decide what makes a line valid, and raise `ValueError` for everything else (also when `json.loads` itself fails). Then `summarise` is a loop that calls it and catches `ValueError` to count skipped lines.

## Hint 2

```text
parse: data = json.loads(line) (ValueError if it fails); must be a dict with request_id, method, uri, status, duration
       upstream_status = str(data.get("upstream_status") or "-")
       tries = 0 if it is "-" or empty else len(upstream_status.split(","))
summarise: for each non-blank line: try parse -> entries else skipped += 1
           by_status counts; slowest = sorted(entries, key=lambda e: (-duration, request_id))[:3]
           share_5xx = (number with 500 <= status <= 599) / requests, or 0.0
```
