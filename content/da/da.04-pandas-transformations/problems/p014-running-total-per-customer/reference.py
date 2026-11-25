import pandas as pd


def running_spend(orders):
    """Sorted copy of orders with a per-customer running total of amount."""
    out = orders.sort_values(["customer_id", "order_date", "order_id"], ignore_index=True)
    out["running_spend"] = out.groupby("customer_id")["amount"].cumsum()
    return out
