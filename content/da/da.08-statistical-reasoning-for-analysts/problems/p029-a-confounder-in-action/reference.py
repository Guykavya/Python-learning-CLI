def confounder_report(df):
    users, others = df[df["app"]], df[~df["app"]]
    return {
        "naive_diff": float(users["spend"].mean() - others["spend"].mean()),
        "engagement_gap": float(users["engagement"].mean() - others["engagement"].mean()),
        "income_gap": float(users["income"].mean() - others["income"].mean()),
    }
