import pandas as pd


def rfm_table(orders, customers, asof):
    asof = pd.Timestamp(asof)
    od = orders[orders["order_date"] <= asof]
    g = od.groupby("customer_id").agg(last=("order_date", "max"), F=("amount", "size"), M=("amount", "sum"))
    g["R"] = (asof - g["last"]).dt.days.astype(int)
    g = g[g.index.isin(customers["customer_id"])]
    return g[["R", "F", "M"]].sort_index()
