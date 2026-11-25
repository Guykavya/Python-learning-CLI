import pandas as pd


def as_of_feature(events, customers):
    m = events.merge(customers[["customer_id", "predict_day"]], on="customer_id", how="inner")
    counts = m[m["day"] < m["predict_day"]].groupby("customer_id").size()
    out = counts.reindex(customers["customer_id"], fill_value=0).astype(int)
    out.name = "events_before"
    return out
