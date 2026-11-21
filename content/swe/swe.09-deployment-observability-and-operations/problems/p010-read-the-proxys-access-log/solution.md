## Approach

```python
def parse_access_line(line):
    try:
        data = json.loads(line)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"not JSON: {exc}") from None
    if not isinstance(data, dict):
        raise ValueError("an access line is a JSON object")
    missing = [key for key in REQUIRED if key not in data]
    if missing:
        raise ValueError(f"missing {', '.join(missing)}")
    upstream_status = str(data.get("upstream_status") or "-")
    tries = 0 if upstream_status.strip() in ("", "-") else len(upstream_status.split(","))
    return {...}


def summarise(lines):
    entries, skipped = [], 0
    for line in lines:
        if not line.strip():
            continue
        try:
            entries.append(parse_access_line(line))
        except (ValueError, TypeError):
            skipped += 1
    ...
```

What the numbers tell you (chapter 7.4): a 5xx share above a few percent means look at the backend; `upstream_tries` of 3 on a 504 means Nginx retried a slow request on every replica (so it ran three times); `502` with 0 tries means nothing answered at all (stale address, crashed process).

## Complexity

O(n log n) for the sort of the entries; one pass for the counts. For a very large log keep only the 3 slowest with `heapq.nlargest`.

## Another way

`jq` does this in one line per question (chapter 8.3): `jq -sc '[.[] | select(.status >= 500)] | length'`. The Python version is what you keep when the questions grow: a test, an alert, a report.
