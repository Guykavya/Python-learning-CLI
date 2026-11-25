import numpy as np
import pandas as pd


def priority(df):
    conditions = [
        df["overdue_days"] > 30,
        df["vip"] & (df["overdue_days"] > 0),
        df["amount"] >= 5000,
    ]
    values = ["urgent", "high", "medium"]
    return pd.Series(np.select(conditions, values, default="low"), index=df.index, name="priority")
