import pandas as pd


def reconcile(parts, total, label="", tol=0.01, strict=False):
    """(ok, difference): do the parts add up to the total within tol? strict=True raises ValueError when not."""
    # TODO: sum via pd.Series, round the difference to 2 decimals (no -0.0), compare with tol
    raise NotImplementedError
