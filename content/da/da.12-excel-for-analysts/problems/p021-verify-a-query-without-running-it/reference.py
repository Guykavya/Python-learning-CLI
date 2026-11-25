def fingerprint_table(df, keys=()):
    fp = {"rows": len(df), "columns": list(df.columns)}
    for c in df.select_dtypes("number").columns:
        fp[f"sum({c})"] = round(float(df[c].sum()), 4)
    for c in df.columns:
        fp[f"blank({c})"] = int(df[c].isna().sum())
    for k in keys:
        fp[f"distinct({k})"] = int(df[k].nunique())
    return fp


def compare_fingerprints(a, b):
    out = []
    for k, v in a.items():
        if k not in b:
            out.append(f"{k}: only in the first")
        elif v != b[k]:
            out.append(f"{k}: {v} against {b[k]}")
    out += [f"{k}: only in the second" for k in b if k not in a]
    return out
