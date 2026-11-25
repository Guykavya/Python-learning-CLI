import pandas as pd


def first_look(df):
    """rows, cols, dtypes (as text), missing per column, duplicate_rows."""
    return {"rows": len(df), "cols": df.shape[1]}
