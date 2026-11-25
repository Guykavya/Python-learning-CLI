def log_step(log, name, before, after, note=""):
    """Append one entry to `log` and return `after` (so steps can be chained)."""
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
    """The log as plain text: a header line, then one line per step."""
    lines = ["step | rows_before | rows_after | dropped | note"]
    for e in log:
        lines.append(f"{e['step']} | {e['rows_before']} | {e['rows_after']} | {e['dropped']} | {e['note']}")
    return "\n".join(lines)
