def mask_email(email):
    """'asha@example.com' -> 'a***@example.com'; None -> None; malformed -> '***'."""
    raise NotImplementedError("strip and lower, split at the last '@', keep the first letter and the domain")


def select_columns(row, allowed):
    """A NEW dict with only the allowed keys, in the order of allowed."""
    raise NotImplementedError("loop over allowed, not over row")


def prepare_export(rows, allowed):
    """Allowed columns only, with any email masked. Never change the input rows."""
    raise NotImplementedError("select_columns, then mask the email if it was kept")
