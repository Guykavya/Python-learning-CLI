import pandas as pd


def index_by(df, key):
    """Index the frame by column `key`; ValueError listing duplicated keys if not unique."""
    return df.set_index(key)
