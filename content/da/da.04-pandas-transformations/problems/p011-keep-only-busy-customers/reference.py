import pandas as pd


def busy_customers(orders, min_orders):
    """All rows of customers with at least min_orders orders."""
    return orders.groupby("customer_id").filter(lambda d: len(d) >= min_orders)
