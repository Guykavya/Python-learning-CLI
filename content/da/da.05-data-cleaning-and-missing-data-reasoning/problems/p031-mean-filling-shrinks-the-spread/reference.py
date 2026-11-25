import pandas as pd


def fill_with_mean(s):
    filled = s.fillna(s.mean())
    return filled, float(s.std()), float(filled.std())
