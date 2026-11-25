import pandas as pd


def reconcile(parts, total, label="", tol=0.01, strict=False):
    """(ok, difference): do the parts add up to the total within tol? strict=True raises ValueError when not."""
    s = float(pd.Series(parts).sum())
    diff = round(s - total, 2) + 0.0
    ok = abs(diff) <= tol
    if strict and not ok:
        raise ValueError(f"{label}: parts={s:,.2f} total={total:,.2f} diff={diff:,.2f}")
    return bool(ok), diff
