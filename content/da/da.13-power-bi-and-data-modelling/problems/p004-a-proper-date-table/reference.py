import pandas as pd


def date_table(start, end):
    start, end = pd.Timestamp(start), pd.Timestamp(end)
    if end < start:
        raise ValueError("end is before start")
    d = pd.date_range(start.normalize(), end.normalize(), freq="D")
    return pd.DataFrame({"DateKey": d.strftime("%Y%m%d").astype(int), "Date": d, "Year": d.year,
                         "Quarter": "Q" + d.quarter.astype(str), "MonthNum": d.month,
                         "MonthName": d.strftime("%b"), "YearMonth": d.strftime("%Y-%m")})
