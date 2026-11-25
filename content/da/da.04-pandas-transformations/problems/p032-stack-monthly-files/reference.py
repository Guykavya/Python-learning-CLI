import pandas as pd


def stack_months(frames):
    """Stack {month: frame} into one table with a first column `month` and a fresh index."""
    pieces = [frame.assign(month=key) for key, frame in frames.items()]
    out = pd.concat(pieces, ignore_index=True)
    rest = [c for c in out.columns if c != "month"]
    return out[["month"] + rest]
