def check_grain(df, key, name=""):
    key = [key] if isinstance(key, str) else list(key)
    missing = int(df[key].isna().any(axis=1).sum())
    if missing:
        raise ValueError(f"{name}: key {key} has {missing} rows with a missing value")
    dup_mask = df.duplicated(subset=key, keep=False)
    n_dup = int(df.duplicated(subset=key).sum())
    if n_dup:
        values = df.loc[dup_mask, key].drop_duplicates()
        if len(key) == 1:
            examples = values[key[0]].tolist()[:5]
        else:
            examples = [tuple(r) for r in values.to_numpy().tolist()][:5]
        raise ValueError(f"{name}: key {key} is not unique: {n_dup} duplicate rows, e.g. {examples}")
    return True
