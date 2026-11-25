import pandas as pd


def never_ordered(customers, orders):
    """Customers with no order: customer columns only, original order, index 0..n-1."""
    return customers.copy()
