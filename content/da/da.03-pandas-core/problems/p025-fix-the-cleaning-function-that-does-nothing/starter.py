def clean(df):
    """Negative quantities are entry errors: make them 0. Round every price to 2 decimals."""
    df[df["qty"] < 0]["qty"] = 0
    for i in range(len(df)):
        df["price"][i] = round(df["price"][i], 2)
    return df
