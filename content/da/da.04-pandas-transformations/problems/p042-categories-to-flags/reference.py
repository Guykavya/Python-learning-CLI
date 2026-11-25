import pandas as pd


def channel_flags(orders):
    """Replace `channel` by 0/1 integer columns ch_<value>, one per channel, after the other columns."""
    return pd.get_dummies(orders, columns=["channel"], prefix="ch", dtype=int)
