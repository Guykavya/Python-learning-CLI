def assert_rows_unchanged(before, after, label):
    n_before, n_after = len(before), len(after)
    if n_after > n_before:
        raise AssertionError(f"fan-out in {label}: {n_before} → {n_after} rows")
    if n_after < n_before:
        raise AssertionError(f"rows lost in {label}: {n_before} → {n_after} rows")
    return after
