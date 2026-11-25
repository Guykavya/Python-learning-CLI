import pandas as pd

CONTRACTS = ("month", "year", "two_year")


def build_features(raw):
    """The ONE feature function for training and serving: fixed columns, fixed order, same index."""
    raise NotImplementedError
