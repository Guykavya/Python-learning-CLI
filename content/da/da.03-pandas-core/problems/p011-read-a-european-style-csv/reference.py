import pandas as pd


def read_shop_csv(path):
    """Read a ';'-separated file with ',' decimals, '.' thousands, '-' as missing, dd.mm.yyyy dates."""
    return pd.read_csv(
        path,
        sep=";",
        decimal=",",
        thousands=".",
        na_values=["-"],
        parse_dates=["date"],
        date_format="%d.%m.%Y",
    )
