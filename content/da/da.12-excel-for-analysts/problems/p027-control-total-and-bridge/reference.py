import pandas as pd


def bridge(df, regions, valid_codes):
    units = df["units"].map(float)
    rev = units * df["unit_price"] * (1 - df["discount"])
    code_bad = ~df["product_code"].map(lambda c: str(c).upper() in valid_codes)
    ok_regions = {r.lower() for r in regions}
    region_bad = ~df["region"].map(lambda r: str(r).lower() in ok_regions)
    control = float(rev.sum())
    grid = float(rev[~code_bad & ~region_bad].sum())
    causes = {"product code not found": float(rev[code_bad].sum()),
              "region not matched": float(rev[~code_bad & region_bad].sum())}
    gap = control - grid
    return {"control_total": control, "grid_total": grid, "gap": gap, "causes": causes,
            "unexplained": gap - sum(causes.values())}
