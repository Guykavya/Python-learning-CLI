import pandas as pd


def draw(pop, n, rng):
    idx = rng.choice(len(pop), n, replace=False)
    return pop.iloc[idx]
