import pandas as pd


def rank_sellers(df):
    return df.sort_values(["revenue", "seller"], ascending=[False, True], na_position="last", kind="stable")
