def clean(df):
    """Negative quantities are entry errors: make them 0. Round every price to 2 decimals."""
    out = df.copy()
    out.loc[out["qty"] < 0, "qty"] = 0
    out["price"] = out["price"].round(2)
    return out
