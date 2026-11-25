import pandas as pd


def never_ordered(customers, orders):
    """Customers with no order: customer columns only, original order, index 0..n-1."""
    mask = ~customers["customer_id"].isin(orders["customer_id"])
    return customers[mask].reset_index(drop=True)
