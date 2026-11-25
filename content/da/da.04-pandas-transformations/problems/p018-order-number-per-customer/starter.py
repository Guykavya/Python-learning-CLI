import pandas as pd


def number_orders(orders):
    """Copy of orders (same order, same index) with order_no = 1, 2, ... per customer in time order."""
    return orders.copy()


def first_orders(orders):
    """Each customer's first order, sorted by customer_id, index 0..n-1."""
    return orders.iloc[:0].copy()
