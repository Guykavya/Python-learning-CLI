import pandas as pd


def safe_merge(left, right, on, how="left", validate="m:1", measure=None, name="",
               expect_same_rows=True, ledger=None):
    """Merge with validate=, record row counts / unmatched keys / measure totals, then guard rows and money."""
    keys = [on] if isinstance(on, str) else list(on)
    null_keys = int(left[keys].isna().any(axis=1).sum())
    out = left.merge(right, on=on, how=how, validate=validate, indicator=True)
    lonely = out.loc[out["_merge"] == "left_only", keys].dropna()
    if len(keys) == 1:
        unmatched_keys = sorted(set(lonely[keys[0]].tolist()))
    else:
        unmatched_keys = sorted(set(lonely.itertuples(index=False, name=None)))
    unmatched = int((out["_merge"] == "left_only").sum())
    out = out.drop(columns="_merge")
    step = name or f"merge on {keys}"
    record = {"step": step, "left_rows": len(left), "right_rows": len(right), "result_rows": len(out),
              "unmatched_left": unmatched, "unmatched_keys": unmatched_keys, "null_keys_left": null_keys}
    if measure is not None:
        record["measure_before"] = round(float(left[measure].sum()), 2)
        record["measure_after"] = round(float(out[measure].sum()), 2)
    if ledger is not None:
        ledger.append(record)
    if how == "left" and expect_same_rows:
        assert len(out) == len(left), f"{step}: row count changed {len(left)} -> {len(out)}"
    if measure is not None:
        before, after = record["measure_before"], record["measure_after"]
        assert abs(after - before) < 0.01, f"{step}: {measure} total changed {before} -> {after}"
    return out
