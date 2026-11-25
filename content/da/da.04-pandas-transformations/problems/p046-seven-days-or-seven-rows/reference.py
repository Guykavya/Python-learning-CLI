import pandas as pd


def rolling_week(daily):
    """Rows sorted by date with week_total = revenue of the 7 calendar days ending on each date."""
    d = daily.sort_values("date").reset_index(drop=True)
    week = d.set_index("date")["revenue"].rolling("7D").sum()
    return d.assign(week_total=week.to_numpy())
