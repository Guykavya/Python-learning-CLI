def both_ways(name, pandas_value, sql, con):
    row = con.execute(sql).fetchone()
    value = None if row is None else row[0]
    p = f"{float(pandas_value):,.2f}"
    if value is None:
        raise AssertionError(f"{name}: MISMATCH pandas={p} sql=None")
    s = f"{float(value):,.2f}"
    if abs(float(pandas_value) - float(value)) > 0.005:
        raise AssertionError(f"{name}: MISMATCH pandas={p} sql={s}")
    return f"{name}: pandas={p} sql={s} MATCH"
