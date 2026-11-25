import pandas as pd


def flag_impossible(df, rules):
    """Return (flags, counts): a Boolean frame of impossible values and a dict of counts per rule."""
    raise NotImplementedError("one Boolean column per rule; None means no limit; missing is not impossible")
