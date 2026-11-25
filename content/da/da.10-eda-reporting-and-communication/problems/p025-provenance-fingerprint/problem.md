# Provenance fingerprint

Chapter section 7.3. A report must be able to say **what it was built from**. A short **fingerprint** of each input table settles most "why are our numbers different?" arguments in a second:
same fingerprint, same data.

Write two functions:

- `fingerprint(df)`: `hashlib.sha256` of the bytes of `pd.util.hash_pandas_object(df, index=False)`, as a hex string, **first 10 characters**.
- `provenance(frames, analysis_date, date_col="week")`: `frames` is a dict `{name: DataFrame}`. Return

```python
{"rows": {name: number of rows, ...},
 "fingerprints": {name: fingerprint, ...},
 "date_from": "YYYY-MM-DD", "date_to": "YYYY-MM-DD",       # min and max of date_col over the frames that have it
 "analysis_date": analysis_date}
```

If no frame has `date_col`, `date_from` and `date_to` are `None`.

The exact hex value depends on the pandas version, so the tests check **properties**: the same data give the same fingerprint, one changed cell gives a different one, and so does a different row order.

## Example

`provenance({"panel": panel, "customers": customers}, "2025-01-06")` gives row counts, two 10-character fingerprints and the date range of `panel["week"]`.
