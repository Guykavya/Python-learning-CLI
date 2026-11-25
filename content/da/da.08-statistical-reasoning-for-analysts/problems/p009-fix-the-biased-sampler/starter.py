import pandas as pd


def draw(pop, n, rng):
    ordered = pop.sort_values("signup_day")
    sample = ordered.iloc[: n - 1]                  # the n - 1 oldest customers
    return pd.concat([sample, sample.iloc[[0]]])    # an off-by-one "fix" that repeats a row
