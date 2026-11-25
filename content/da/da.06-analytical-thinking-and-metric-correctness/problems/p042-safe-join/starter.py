def safe_join(left, right, on, how="left", validate="m:1", label=""):
    """merge with a relationship check and a row-count check (see problem.md)."""
    raise NotImplementedError("merge with validate=..., then compare len(left) and len(result) for a left join")
