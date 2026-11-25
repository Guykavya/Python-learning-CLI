import pandas as pd

CODE = r"^(?P<category>[A-Z]{2})-(?P<year>[0-9]{4})-(?P<number>[0-9]{4})$"


def split_product_code(s):
    """Product codes like EL-2024-0042 split into category, year and number columns."""
    parts = s.str.strip().str.extract(CODE)
    parts["year"] = pd.to_numeric(parts["year"]).astype("Int64")
    parts["number"] = pd.to_numeric(parts["number"]).astype("Int64")
    return parts
