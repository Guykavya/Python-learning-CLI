def missingness_gap(df, col, other):
    m = df[col].isna()
    missing_mean = float(df.loc[m, other].mean())
    present_mean = float(df.loc[~m, other].mean())
    return {"missing_mean": missing_mean, "present_mean": present_mean, "gap": missing_mean - present_mean}
