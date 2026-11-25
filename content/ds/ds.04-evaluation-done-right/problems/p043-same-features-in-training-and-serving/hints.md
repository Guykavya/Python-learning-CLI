## Hint 1

Why does `pd.get_dummies` break when you score one customer at a time? Write each contract column as an explicit comparison instead.

## Hint 2

```text
out = DataFrame(index=raw.index)
out["tenure_months"] = raw["tenure_months"].clip(1, 72)
out["charge_per_call"] = raw["monthly_charge"] / (1 + raw["support_calls"])
for level in ("month", "year", "two_year"): out[f"contract_{level}"] = (raw["contract"] == level).astype(int)
out["autopay"] = raw["autopay"].astype(int)
```
