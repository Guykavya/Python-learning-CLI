def safe_join(left, right, on, how="left", validate="m:1", label=""):
    out = left.merge(right, on=on, how=how, validate=validate)
    if how == "left" and len(out) != len(left):
        name = label or f"join on {on}"
        raise AssertionError(f"{name}: rows changed {len(left)} -> {len(out)} (fan-out or a lost key?)")
    return out
