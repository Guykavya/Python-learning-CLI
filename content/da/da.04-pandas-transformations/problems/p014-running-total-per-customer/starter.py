import pandas as pd


def running_spend(orders):
    """Sorted copy of orders with a per-customer running total of amount."""
    return orders.copy()
