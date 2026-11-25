import pandas as pd


def tap(d, label, log):
    """Append (label, d.shape) to log and return d unchanged."""
    # TODO
    raise NotImplementedError


def clean_items(items, log):
    """One chain: start -> valid qty -> no duplicates -> with revenue -> per order, tapping after each step."""
    # TODO: (items.pipe(tap, "start", log) .loc[...] .pipe(tap, ...) ...)
    raise NotImplementedError
