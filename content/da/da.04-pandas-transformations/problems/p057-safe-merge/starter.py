import pandas as pd


def safe_merge(left, right, on, how="left", validate="m:1", measure=None, name="",
               expect_same_rows=True, ledger=None):
    """Merge with validate=, record row counts / unmatched keys / measure totals, then guard rows and money."""
    # TODO: see problem.md: merge with indicator=True, build the record, append it, then the two guards
    raise NotImplementedError
