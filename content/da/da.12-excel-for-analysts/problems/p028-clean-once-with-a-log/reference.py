import pandas as pd


def clean_orders(df, regions, valid_codes):
    c = df.copy()
    c["region"] = c["region"].astype(str).str.strip().str.title()
    c["units"] = pd.to_numeric(c["units"], errors="coerce")
    code = c["product_code"].astype(str).str.strip().str.upper()
    code = code.str.replace(r"^PO(\d)$", r"P0\1", regex=True).str.replace(r"^P(\d)$", r"P0\1", regex=True)
    c["product_code"] = code
    bad = ~c["region"].isin(regions) | c["units"].isna() | ~c["product_code"].isin(valid_codes)
    rules = {"region": "region: strip and proper case", "units": "units: text to number", "product_code": "product_code: strip, upper case, zero-pad"}
    rows = []
    for i in c.index[~bad]:
        for field in ("region", "units", "product_code"):
            old, new = df.at[i, field], c.at[i, field]
            changed = isinstance(old, str) if field == "units" else str(old) != str(new)
            if changed:
                rows.append({"row": i, "field": field, "old": old, "new": new, "rule": rules[field]})
    log = pd.DataFrame(rows, columns=["row", "field", "old", "new", "rule"])
    return c[~bad].reset_index(drop=True), df[bad], log
