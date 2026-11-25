import numpy as np
import pandas as pd


def age_bands(s):
    return pd.cut(s, bins=[0, 18, 40, 65, np.inf], labels=["youth", "adult", "middle", "senior"], include_lowest=True)


def spend_quartiles(s):
    return pd.qcut(s, q=4, labels=["Q1", "Q2", "Q3", "Q4"])
