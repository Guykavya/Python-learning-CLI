import numpy as np
import pandas as pd


def two_ways(df):
    band = pd.cut(df["age"], [-np.inf, 30, 45, np.inf], right=False)
    complete = df.groupby("city")["income"].mean()
    band_median = df.groupby(band, observed=True)["income"].transform("median")
    filled = df["income"].fillna(band_median).groupby(df["city"]).mean()
    complete.name = filled.name = "income"
    return {"complete": complete, "filled": filled, "max_diff": float((filled - complete).abs().max())}
