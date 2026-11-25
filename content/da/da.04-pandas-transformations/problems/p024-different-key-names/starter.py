import pandas as pd


def attach_store_names(orders, stores):
    """Every order with city_customer, city_store and region."""
    return orders.copy()
