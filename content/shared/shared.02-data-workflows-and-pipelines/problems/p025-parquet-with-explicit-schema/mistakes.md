- Letting pyarrow infer the schema. It works on the first test batch and then gives a `null` column
  for an all-`None` batch, a different decimal precision per file, and the source's time-zone
  offset instead of UTC. Files from different days stop fitting together.
- Using `pa.float64()` for money. `0.1 + 0.2 != 0.3` in floats; amounts must be exact, so use
  `decimal128(precision, scale)` (or integer cents).
- Using `pa.timestamp("us")` without `tz`. The column then holds "wall clock" times with no zone,
  and you read back naive datetimes that cannot be compared with aware ones.
- Trusting pyarrow to catch naive datetimes. It does not; it assumes UTC. Check `tzinfo` yourself.
- Checking for naive datetimes *after* writing, so a bad batch still leaves a file on disk.
- Rounding amounts yourself (`round(amount, 2)`) to make the `ArrowInvalid` go away. The error is
  telling you the data does not match the contract; hiding it loses money.
- Forgetting that the schema must also be used for an empty batch: `pa.Table.from_pylist([])`
  without a schema has no columns at all.
