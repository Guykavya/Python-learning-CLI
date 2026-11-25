import pandas as pd

FOREVER = pd.Timestamp("2999-12-31")


def scd2_apply(dim, changes, as_of):
    """New dimension table with the old rows closed and new current rows added (type 2); dim is not modified."""
    raise NotImplementedError


def lookup_key(dim, customer_id, date):
    """SurrogateKey of the version valid on the date; ValueError('no version valid on that date') if none."""
    raise NotImplementedError
