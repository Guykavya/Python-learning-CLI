import pandas as pd


def snake(name):
    return name.strip().lower().replace(" ", "_")


def prepare(df):
    return (df.rename(columns=snake)
              .loc[:, lambda d: ~d.columns.str.startswith("tmp_")]
              .assign(revenue=lambda d: d["qty"] * d["unit_price"]))
