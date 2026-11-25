## Model answer

1. **Why floats.** A classic integer column is a NumPy `int64` block: 8 raw bytes per value, and every bit pattern is a real number, so there is **no spare value** that can mean "missing". A float block does have one: `NaN` ("not a number") is a special float. So when pandas sees `[1, None, 3]` it picks the only NumPy type that can hold both the numbers and a gap: `float64`. The numbers `1.0` and `3.0` are exact, but the column is no longer integers (and very large ids above 2**53 would lose digits as floats).

2. **What `Int64` changes.** The capitalised nullable dtypes store the values **plus a separate mask** saying which entries are missing. The values stay integers, and the gap is a real marker, `pd.NA`, which prints as `<NA>`. Comparisons with `pd.NA` give "unknown" (`<NA>`), not `False`, so a missing value is not silently treated as "not greater". The price: they are a little slower and use a little more memory than plain `int64`, some older code and libraries do not understand `pd.NA`, and arithmetic with `pd.NA` gives `<NA>`.

3. **When to convert.** **After cleaning.** First turn the text into numbers (`to_numeric(errors="coerce")`), look at what became missing, and decide what the gaps mean. Then make the final dtype choice: `Int64` when the values are counts or ids and the gaps must stay visible; plain `int64` only when no gap is left. Converting early hides problems, and `astype("int64")` on a column that still has a gap raises an error.

**Checklist: your answer should mention**
- [ ] `int64` has no bit pattern for missing
- [ ] `NaN` is a float, so the column becomes `float64`
- [ ] nullable dtype `Int64` keeps integers and stores gaps as `pd.NA`
- [ ] `pd.NA` comparisons give "unknown", not `False`
- [ ] cost: speed, memory, library support
- [ ] convert after cleaning, once you know what the gaps mean
