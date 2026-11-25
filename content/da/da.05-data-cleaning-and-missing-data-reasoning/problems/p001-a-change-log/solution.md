## Approach

`log_step` only reads two lengths and appends a small dict; it never touches the data. Returning `after` lets a
cleaning script read like a recipe, one logged step per line. `show_log` turns the dicts into one line each, so the
log can be pasted into a report or printed at the end of a run. Using `max(0, ...)` keeps the "dropped" column honest
for steps that add rows.

## Code

```python
def log_step(log, name, before, after, note=""):
    rows_before = len(before)
    rows_after = len(after)
    log.append({
        "step": name,
        "rows_before": rows_before,
        "rows_after": rows_after,
        "dropped": max(0, rows_before - rows_after),
        "note": note,
    })
    return after


def show_log(log):
    lines = ["step | rows_before | rows_after | dropped | note"]
    for e in log:
        lines.append(f"{e['step']} | {e['rows_before']} | {e['rows_after']} | {e['dropped']} | {e['note']}")
    return "\n".join(lines)
```

## Complexity

`log_step` is O(1) (`len` of a frame is constant time). `show_log` is O(k) for k log entries.

## Another way

The chapter returns `pd.DataFrame(LOG)` and also counts missing cells before and after. A frame is nicer to filter
(`log[log.dropped > 0]`); the plain-text version needs no pandas at all and works in a text report. Keeping the log as
a list of dicts is what makes both possible.
