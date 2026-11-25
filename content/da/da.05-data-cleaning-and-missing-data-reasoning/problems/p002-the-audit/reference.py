import pandas as pd


def audit(df):
    """One row per column: dtype, missing, unique, top and suspect_text."""
    rows = []
    for name in df.columns:
        s = df[name]
        present = s.dropna()
        top = None
        if len(present) > 0:
            counts = present.value_counts()
            best = counts.max()
            top = sorted(counts[counts == best].index)[0]
        suspect = 0
        if pd.api.types.is_string_dtype(s) and len(present) > 0:
            parsed = pd.to_numeric(present.str.strip(), errors="coerce")
            ok = parsed.notna()
            if ok.sum() * 2 > len(present):
                suspect = int((~ok).sum())
        rows.append({
            "dtype": str(s.dtype),
            "missing": int(s.isna().sum()),
            "unique": int(present.nunique()),
            "top": top,
            "suspect_text": suspect,
        })
    return pd.DataFrame(rows, index=list(df.columns), columns=["dtype", "missing", "unique", "top", "suspect_text"])
