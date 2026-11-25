import pandas as pd


def channel_flags(orders):
    """Replace `channel` by 0/1 integer columns ch_<value>, one per channel, after the other columns."""
    # TODO: one pd.get_dummies call (columns=, prefix=, dtype=)
    raise NotImplementedError
