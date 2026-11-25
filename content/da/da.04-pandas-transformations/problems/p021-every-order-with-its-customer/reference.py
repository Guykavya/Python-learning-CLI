import pandas as pd


def orders_with_customers(orders, customers):
    """Return (every order with city and segment, number of orders with an unknown customer)."""
    table = orders.merge(customers, on="customer_id", how="left", validate="m:1", indicator=True)
    unknown = int((table["_merge"] == "left_only").sum())
    return table.drop(columns="_merge"), unknown
