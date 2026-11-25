import pandas as pd


def validate_table(df, rules):
    """Return [(rule name, number failed, first index labels), ...] for the rules that fail."""
    raise NotImplementedError("run each rule, find the False rows, report count and the first three labels")
