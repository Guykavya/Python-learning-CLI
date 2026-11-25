# Convert, and count what was lost

Chapter sections 10.3 and 11. `pd.to_numeric(s, errors="coerce")` turns anything it cannot read into `NaN` **without saying
so**. A cleaning step that hides what it threw away is dangerous: you must report it.

`s` is a Series of raw text (some values are missing). Write `convert_numbers(s)` returning a tuple
`(numbers, bad_values)`:

- `numbers` is a `float64` Series with the same index as `s`: the text **after stripping spaces**, converted with
  `to_numeric(errors="coerce")`;
- `bad_values` is a sorted list of the distinct (stripped) texts that were **not empty** (not missing, not `""`, not only
  spaces) but still could not be read as a number.

The input is not changed.

## Example

```python
s = pd.Series(["12", " 3.5 ", "abc", "", None, "1,000", "abc", "7"])
numbers, bad = convert_numbers(s)
numbers.tolist()    # [12.0, 3.5, nan, nan, nan, nan, nan, 7.0]
bad                 # ['1,000', 'abc']
```

Empty and missing values become `NaN` too, but they are *not* reported: they had no value to lose.
