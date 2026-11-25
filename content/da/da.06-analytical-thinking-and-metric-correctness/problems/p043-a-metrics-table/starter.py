import pandas as pd


def metrics_table(ctx, specs, months):
    """One row per metric and month: metric, month, unit, numerator, denominator, value (see problem.md)."""
    raise NotImplementedError("loop over specs and months, call spec.fn(ctx, start, end), collect one row each")
