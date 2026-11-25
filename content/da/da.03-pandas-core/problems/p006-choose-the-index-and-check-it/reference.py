import pandas as pd


def index_by(df, key):
    """Index the frame by column `key`; ValueError listing duplicated keys if not unique."""
    dup = df[key][df[key].duplicated()].unique().tolist()
    if dup:
        raise ValueError("%s has duplicated keys: %s" % (key, dup))
    return df.set_index(key)
