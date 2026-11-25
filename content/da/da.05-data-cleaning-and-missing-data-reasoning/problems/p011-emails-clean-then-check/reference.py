import pandas as pd


def clean_email(s):
    """Lower-cased, stripped address, or missing when it does not look like an email."""
    e = s.str.strip().str.lower()
    return e.where(e.str.fullmatch(r"[a-z0-9._+-]+@[a-z0-9-]+(\.[a-z0-9-]+)+", na=False))
