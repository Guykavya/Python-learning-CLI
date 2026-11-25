import pandas as pd


def price_at_order(orders, price_history):
    """Each order line with the price in force on its date (latest price on or before it, per product)."""
    left = orders.sort_values("order_date")
    right = price_history.sort_values("effective")
    out = pd.merge_asof(left, right, left_on="order_date", right_on="effective",
                        by="product_id", direction="backward")
    assert len(out) == len(orders)
    return out.drop(columns="effective").sort_values("order_id").reset_index(drop=True)
