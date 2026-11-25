import hashlib

import pandas as pd


def fingerprint(df):
    """First 10 hex characters of sha256 over the row hashes (index ignored)."""
    raise NotImplementedError


def provenance(frames, analysis_date, date_col="week"):
    """{'rows', 'fingerprints', 'date_from', 'date_to', 'analysis_date'} for a dict of DataFrames."""
    raise NotImplementedError
