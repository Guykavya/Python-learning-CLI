# Clean once, with a log

Chapter section 11.5. Fix the dirty data **once**, in Python, and keep a **log** of every change, so that the cleaning can be reviewed and repeated. What cannot be repaired goes to a **quarantine** table, not into the total.

Write `clean_orders(df, regions, valid_codes)`. `df` has `region`, `units` (numbers or text) and `product_code`, plus other columns that you keep unchanged. Apply these rules to a copy:

1. **region**: strip spaces and apply `str.title()`; rule text `region: strip and proper case`;
2. **units**: a string is converted with `pd.to_numeric(errors="coerce")`; rule text `units: text to number`;
3. **product_code**: `str.strip().upper()`, then `P` followed by a **single** digit is zero-padded (`P7` becomes `P07`), and the letter O in the digit position is read as a zero (`PO5` becomes `P05`); rule text `product_code: strip, upper case, zero-pad`.

After the rules, a row is **bad** if its region is not in `regions`, its units are `NaN`, or its code is not in `valid_codes`. Return `(clean, quarantine, log)`:

- `clean`: the good rows, cleaned, with the index reset;
- `quarantine`: the bad rows **exactly as they were** in `df` (original index kept);
- `log`: a DataFrame with the columns `row` (the original index), `field`, `old`, `new`, `rule`: one entry per **changed cell of a good row**, ordered by row and then in the field order region, units, product_code. A value that did not change has no entry; for `units`, an entry exists only when the original was **text** (an int that becomes a float is not a change).

The checker evaluates formulas with a small Excel evaluator (MiniXL, from the chapter): it knows SUM, AVERAGE, COUNT, COUNTA, MIN, MAX, ABS, ROUND, IF, IFERROR, IFNA, ISERROR, TRIM, TEXT, DATE, YEAR, MONTH, SUMIFS, COUNTIFS, AVERAGEIFS, SUMIF, COUNTIF, LARGE, MATCH, INDEX, XLOOKUP and VLOOKUP. Use only these functions.

## Example

The row `region="north "`, `units="7"`, `product_code="p7"` gives three log entries: `north ` -> `North`, `7` -> `7.0`, `p7` -> `P07`.
