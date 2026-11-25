from pathlib import Path

import pandas as pd

START, END = pd.Timestamp("2025-01-01"), pd.Timestamp("2025-06-30")
TRUE = ("yes", "y", "true", "1")
FALSE = ("no", "n", "false", "0")
FORMATS = ("%Y-%m-%d", "%d/%m/%Y", "%b %d, %Y")


def tidy_text(s, case="title"):
    t = s.astype("string").str.strip().str.replace(r"\s+", " ", regex=True)
    return t.str.title() if case == "title" else t.str.lower()


def to_money(s):
    txt = (s.astype("string").str.replace(r"(?i)rs\.?|₹|inr", "", regex=True)
            .str.replace(",", "", regex=False).str.strip())
    return pd.to_numeric(txt, errors="coerce")


def to_percent(s):
    num = pd.to_numeric(s.astype("string").str.replace("%", "", regex=False).str.strip(), errors="coerce")
    return num.where(num <= 1, num / 100)


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


def load_sales(path):
    raw = pd.read_csv(path, dtype="str", encoding="utf-8")
    removed = int(raw.duplicated().sum())
    df = raw.drop_duplicates(ignore_index=True)
    df["customer"] = tidy_text(df["customer"])
    df["city"] = tidy_text(df["city"])
    df["product"] = tidy_text(df["product"], case="lower")
    df["category"] = tidy_text(df["category"], case="lower")
    df["unit_price"] = to_money(df["unit_price"])
    df["discount"] = to_percent(df["discount"])
    df["order_date"] = to_date(df["order_date"])
    df["paid"] = to_bool(df["paid"])
    df["qty"] = to_int(df["qty"])
    return df, removed


def add_flags(df):
    out = df.copy()
    out["flag_date"] = ~out["order_date"].between(START, END)
    out["flag_qty"] = ~out["qty"].between(1, 50).fillna(False)
    out["flag_price"] = ~out["unit_price"].between(10, 20_000).fillna(False)
    out["flag_id"] = out.duplicated(subset=["order_id"], keep=False)
    flags = out.filter(like="flag_")
    out["usable"] = ~flags.any(axis=1)
    out["revenue"] = out["qty"] * out["unit_price"] * (1 - out["discount"].fillna(0))
    return out


def explore(path, out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    df, removed = load_sales(path)
    sales = add_flags(df)
    sales.to_parquet(out_dir / "clean.parquet", index=False)

    flags = sales.filter(like="flag_")
    register = pd.DataFrame({
        "problem": ["exact_duplicates_removed", "flag_date", "flag_qty", "flag_price", "flag_id", "any_flag"],
        "rows": [removed] + [int(flags[c].sum()) for c in flags.columns] + [int(flags.any(axis=1).sum())],
    })
    register.to_csv(out_dir / "problems.csv", index=False)

    ok = sales[sales["usable"]]
    revenue = float(ok["revenue"].sum())
    by_month = ok.set_index("order_date")["revenue"].resample("MS").sum()
    best_month = by_month.idxmax().strftime("%Y-%m")
    top5 = ok.sort_values(["revenue", "order_id"], ascending=[False, True])["order_id"].head(5).tolist()
    weekdays = ok["order_date"].dt.day_name().value_counts()
    busiest = sorted(weekdays.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
    paid_revenue = ok.loc[ok["paid"] == True, "revenue"].sum()
    gross = (ok["qty"] * ok["unit_price"]).sum()
    return {
        "revenue": revenue,
        "best_month": best_month,
        "top5": top5,
        "busiest_weekday": busiest,
        "unpaid_share": float((ok["revenue"].sum() - paid_revenue) / ok["revenue"].sum()),
        "discount_cost_share": float((gross - ok["revenue"].sum()) / gross),
    }
