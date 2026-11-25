import pandas as pd


def days_between_orders(orders):
    """Sorted copy of orders with days_since_prev (NaN for a customer's first order)."""
    out = orders.sort_values(["customer_id", "order_date", "order_id"], ignore_index=True)
    out["days_since_prev"] = out.groupby("customer_id")["order_date"].diff().dt.days
    return out
