import pandas as pd


def to_money(s):
    """Text such as 'Rs. 1,250.50' -> 1250.5. Anything that is not a number -> missing."""
    # TODO: remove currency marks and commas, strip, then pd.to_numeric(errors="coerce")
    raise NotImplementedError
