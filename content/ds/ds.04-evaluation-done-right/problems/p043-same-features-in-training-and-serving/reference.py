import pandas as pd

CONTRACTS = ("month", "year", "two_year")


def build_features(raw):
    out = pd.DataFrame(index=raw.index)
    out["tenure_months"] = raw["tenure_months"].clip(1, 72)
    out["charge_per_call"] = raw["monthly_charge"] / (1 + raw["support_calls"])
    for level in CONTRACTS:
        out[f"contract_{level}"] = (raw["contract"] == level).astype(int)
    out["autopay"] = raw["autopay"].astype(int)
    return out
