import pandas as pd


def profile(df, top=3):
    rows = {}
    for col in df.columns:
        s = df[col]
        pairs = sorted(s.value_counts().items(), key=lambda kv: (-kv[1], kv[0]))[:top]
        numeric = pd.api.types.is_numeric_dtype(s) and not pd.api.types.is_bool_dtype(s)
        rows[col] = {
            "dtype": str(s.dtype),
            "missing": int(s.isna().sum()),
            "unique": int(s.nunique()),
            "top": [(v, int(c)) for v, c in pairs],
            "min": float(s.min()) if numeric and s.notna().any() else float("nan"),
            "max": float(s.max()) if numeric and s.notna().any() else float("nan"),
        }
    return pd.DataFrame.from_dict(rows, orient="index", columns=["dtype", "missing", "unique", "top", "min", "max"])
