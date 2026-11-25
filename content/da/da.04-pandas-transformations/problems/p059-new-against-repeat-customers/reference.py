import pandas as pd


def new_vs_repeat(orders):
    """Per month: new_customers, repeat_customers, new_revenue, repeat_revenue (new = month of first order)."""
    month = orders["order_date"].dt.to_period("M")
    first = orders.groupby("customer_id")["order_date"].transform("min").dt.to_period("M")
    d = orders.assign(month=month.astype(str), kind=(month == first).map({True: "new", False: "repeat"}))
    g = d.groupby(["month", "kind"])
    cust = g["customer_id"].nunique().unstack("kind", fill_value=0).reindex(columns=["new", "repeat"], fill_value=0)
    rev = g["revenue"].sum().unstack("kind", fill_value=0.0).reindex(columns=["new", "repeat"], fill_value=0.0)
    return pd.DataFrame({
        "month": cust.index.to_list(),
        "new_customers": cust["new"].astype("int64").to_numpy(),
        "repeat_customers": cust["repeat"].astype("int64").to_numpy(),
        "new_revenue": rev["new"].astype("float64").to_numpy(),
        "repeat_revenue": rev["repeat"].astype("float64").to_numpy(),
    })
