def split_xy(df, target):
    if target not in df.columns:
        raise KeyError(f"target column '{target}' not found; columns are {list(df.columns)}")
    X = df.drop(columns=[target])
    y = df[target]
    return X, y
