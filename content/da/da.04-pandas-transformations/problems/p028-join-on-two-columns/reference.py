import pandas as pd


def daily_targets(sales, targets):
    """Every sales row with its day's target and hit = revenue >= target."""
    out = sales.merge(targets[["store_id", "date", "target"]], on=["store_id", "date"], how="left", validate="m:1")
    out["hit"] = out["revenue"] >= out["target"]        # a comparison with NaN is False
    return out
