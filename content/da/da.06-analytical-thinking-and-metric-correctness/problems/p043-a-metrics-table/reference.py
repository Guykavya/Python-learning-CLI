import pandas as pd


def metrics_table(ctx, specs, months):
    rows = []
    for spec in specs:
        for label, (start, end) in months.items():
            value, numerator, denominator = spec.fn(ctx, pd.Timestamp(start), pd.Timestamp(end))
            rows.append({"metric": spec.name, "month": label, "unit": spec.unit, "numerator": numerator,
                         "denominator": float("nan") if denominator is None else denominator, "value": value})
    return pd.DataFrame(rows, columns=["metric", "month", "unit", "numerator", "denominator", "value"])
