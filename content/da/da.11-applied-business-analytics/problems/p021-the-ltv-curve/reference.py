import pandas as pd


def ltv_curve(orders, customers, asof, months):
    asof = pd.Timestamp(asof)
    cu = customers[(asof - customers["first_order"]).dt.days >= 30 * months + 29]
    if len(cu) == 0:
        raise ValueError("no customer has a full follow-up")
    o = orders.merge(cu[["customer_id", "first_order"]], on="customer_id", validate="m:1")
    o["b"] = (o["order_date"] - o["first_order"]).dt.days // 30
    per_bucket = o[o["b"] <= months].groupby("b")["amount"].sum().reindex(range(months + 1), fill_value=0.0)
    return (per_bucket.cumsum() / len(cu)).astype(float)
