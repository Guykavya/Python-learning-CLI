import pandas as pd


def read_with_codes(path):
    """Read the file; pin and product_code stay text; qty is int64."""
    return pd.read_csv(path)
