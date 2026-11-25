## Hint 1

What are the three numbers you can get from a frame without a loop? What should `dropped` be when `after` has *more*
rows than `before`: a negative number, or something else? And what must `log_step` return so that chaining works?

## Hint 2

```text
log_step:
    rows_before = len(before); rows_after = len(after)
    log.append({"step": name, "rows_before": ..., "rows_after": ...,
                "dropped": max(0, rows_before - rows_after), "note": note})
    return after
show_log:
    lines = [header]
    for entry in log: lines.append(" | ".join(str(value) for the five fields, in order))
    return "\n".join(lines)
```
