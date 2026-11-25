import pandas as pd


def price_change_effect(df, change_date, treated):
    plans = sorted(df["plan"].unique())
    if len(plans) != 2 or treated not in plans:
        raise ValueError("need exactly two plans, one of them treated")
    control = plans[0] if plans[1] == treated else plans[1]
    after = df["week"] >= pd.Timestamp(change_date)

    def rate(plan, period):
        return df.loc[(df["plan"] == plan) & period, "churn_now"].mean() * 100

    return float((rate(treated, after) - rate(treated, ~after)) - (rate(control, after) - rate(control, ~after)))
