import pandas as pd
import pandera.pandas as pa


def split_valid(df, schema):
    """Return (valid, quarantine): quarantine has the original columns plus a 'reasons' text column."""
    raise NotImplementedError("validate lazily; group failure_cases by row label; split the rows")
