import pandas as pd


def price_at_order(orders, price_history):
    """Each order line with the price in force on its date (latest price on or before it, per product)."""
    # TODO: sort both tables by their time key, then pd.merge_asof(..., by=..., direction="backward")
    raise NotImplementedError
