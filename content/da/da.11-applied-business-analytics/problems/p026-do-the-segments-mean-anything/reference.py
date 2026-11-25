import pandas as pd


def future_value_by_segment(rfm, orders_after):
    fut = orders_after.groupby("customer_id").agg(n=("amount", "size"), spend=("amount", "sum"))
    t = rfm[["segment"]].join(fut).fillna({"n": 0, "spend": 0})
    out = t.groupby("segment").agg(customers=("spend", "size"),
                                   bought_again_pct=("n", lambda s: float((s > 0).mean() * 100)),
                                   future_spend_per_customer=("spend", "mean"))
    out["customers"] = out["customers"].astype(int)
    return out.sort_values("future_spend_per_customer", ascending=False)
