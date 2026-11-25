import pandas as pd


def split_product_code(s):
    """Product codes like EL-2024-0042 split into category, year and number columns."""
    raise NotImplementedError("str.extract with named groups, then convert year and number to Int64")
