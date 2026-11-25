import pandas as pd


def to_money(s):
    txt = (s.astype("string").str.replace(r"(?i)rs\.?|₹|inr", "", regex=True)
            .str.replace(",", "", regex=False).str.strip())
    return pd.to_numeric(txt, errors="coerce")
