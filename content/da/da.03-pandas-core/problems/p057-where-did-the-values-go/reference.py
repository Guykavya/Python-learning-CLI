import pandas as pd


def conversion_losses(raw, clean):
    out = {}
    for col in [c for c in raw.columns if c in clean.columns]:
        text = raw[col].astype("string")
        non_empty = (text.notna() & (text.str.strip() != "")).fillna(False)
        lost = non_empty & clean[col].isna()
        out[col] = {"lost": int(lost.sum()), "examples": text[lost].drop_duplicates().head(3).tolist()}
    return out
