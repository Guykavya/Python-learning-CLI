import numpy as np
import pandas as pd


def line_totals(df):
    discount = np.select([df["qty"] >= 10, df["qty"] >= 5], [0.10, 0.05], default=0.0)
    return pd.Series(df["qty"] * df["unit_price"] * (1 - discount), index=df.index, name="total")
