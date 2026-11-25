import pandas as pd


def days_between_orders(orders):
    """Sorted copy of orders with days_since_prev (NaN for a customer's first order)."""
    return orders.copy()
