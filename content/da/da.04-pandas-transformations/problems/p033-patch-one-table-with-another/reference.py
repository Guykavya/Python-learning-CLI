import pandas as pd


def patch_customers(old, fixes):
    """old corrected by fixes: a fix value wins, a missing fix keeps the old value; rows and columns of old only."""
    base = old.set_index("customer_id")
    base.update(fixes.set_index("customer_id"))
    return base.reset_index()[list(old.columns)]
