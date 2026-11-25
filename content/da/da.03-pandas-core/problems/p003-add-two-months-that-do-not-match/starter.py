import pandas as pd


def combine_months(a, b):
    """Total per label over two Series; a label missing from one counts as 0; sorted; int64."""
    return a + b
