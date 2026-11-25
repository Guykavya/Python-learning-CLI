import pandas as pd

TRUE = ("yes", "y", "true", "1")
FALSE = ("no", "n", "false", "0")
FORMATS = ("%Y-%m-%d", "%d/%m/%Y", "%b %d, %Y")


def to_money(s):
    txt = (s.astype("string").str.replace(r"(?i)rs\.?|₹|inr", "", regex=True)
            .str.replace(",", "", regex=False).str.strip())
    return pd.to_numeric(txt, errors="coerce")


def to_date(s):
    text = s.astype("string").str.strip()
    out = pd.Series(pd.NaT, index=s.index, dtype="datetime64[us]")
    for f in FORMATS:
        out = out.fillna(pd.to_datetime(text, format=f, errors="coerce"))
    return out


def to_bool(s):
    t = s.astype("string").str.strip().str.lower()
    out = pd.Series(pd.NA, index=s.index, dtype="boolean")
    out[t.isin(TRUE).fillna(False)] = True
    out[t.isin(FALSE).fillna(False)] = False
    return out


def to_int(s):
    num = pd.to_numeric(s.astype("string").str.strip(), errors="coerce")
    return num.where(num % 1 == 0).astype("Int64")


def load_sales(path, money=(), dates=(), bools=(), ints=()):
    df = pd.read_csv(path, dtype="str", encoding="utf-8")
    losses = {}
    for cols, convert in ((money, to_money), (dates, to_date), (bools, to_bool), (ints, to_int)):
        for c in cols:
            raw = df[c]
            df[c] = convert(raw)
            losses[c] = int((raw.notna() & df[c].isna()).sum())
    return df, losses
