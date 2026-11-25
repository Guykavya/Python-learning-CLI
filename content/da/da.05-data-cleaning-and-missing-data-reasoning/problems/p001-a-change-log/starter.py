def log_step(log, name, before, after, note=""):
    """Append one entry to `log` and return `after` (so steps can be chained)."""
    raise NotImplementedError("append a dict with step, rows_before, rows_after, dropped, note")


def show_log(log):
    """The log as plain text: a header line, then one line per step."""
    raise NotImplementedError("build the text table described in problem.md")
