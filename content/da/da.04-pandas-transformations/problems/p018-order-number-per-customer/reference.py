import pandas as pd


def number_orders(orders):
    """Copy of orders (same order, same index) with order_no = 1, 2, ... per customer in time order."""
    ordered = orders.sort_values(["customer_id", "order_date", "order_id"])
    order_no = ordered.groupby("customer_id").cumcount() + 1
    return orders.assign(order_no=order_no)          # aligned by index label: original order kept


def first_orders(orders):
    """Each customer's first order, sorted by customer_id, index 0..n-1."""
    numbered = number_orders(orders)
    first = numbered[numbered["order_no"] == 1].drop(columns="order_no")
    return first.sort_values("customer_id", ignore_index=True)
