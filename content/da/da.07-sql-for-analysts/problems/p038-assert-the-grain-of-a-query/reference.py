def assert_grain(con, sql, key):
    df = con.execute(sql).df()
    if df[key].isna().any().any():
        raise AssertionError(f"NULL values in key columns {key}: the grain is wrong")
    dup = df[df.duplicated(subset=key, keep=False)]
    if len(dup):
        examples = dup[key].drop_duplicates().head(3).values.tolist()
        raise AssertionError(f"{len(dup)} rows share duplicate keys, e.g. {examples}: the grain is wrong")
    return df
