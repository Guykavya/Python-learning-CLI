import pandas as pd


def period_totals(daily, freq):
    """Sum daily revenue into bins of `freq` ("W-MON", "ME", ...): columns period, revenue."""
    s = daily.set_index("date")["revenue"].resample(freq).sum()
    return s.rename_axis("period").reset_index()
