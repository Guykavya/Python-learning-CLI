import pandas as pd


def tidy_names(s):
    return s.str.strip().str.replace(r"\s+", " ", regex=True).str.title()
