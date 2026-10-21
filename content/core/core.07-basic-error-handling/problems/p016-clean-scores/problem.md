# Clean scores the EAFP way

A teacher typed test scores into a spreadsheet, and some cells are messy. Write
`clean_scores(tokens)` that returns a tuple `(scores, rejected)`:

- `scores`: every token that `int()` can convert **and** whose value is from 0 to 100, as ints, in
  order.
- `rejected`: every other token, **unchanged**, in order.

Accept exactly what `int()` accepts: `" 7"`, `"+3"` and `"1_0"` are all fine numbers. Section 14
showed that `isdigit()` gets this wrong in both directions, so **do not** use `isdigit`,
`isnumeric` or `isdecimal`. Let `int()` be the check.

**Example**

```python
clean_scores(["88", " 7", "abc", "+3", "-5", "²", "100", "4.0", "", "1_0"])
# ([88, 7, 3, 100, 10], ['abc', '-5', '²', '4.0', ''])
```

`"-5"` is a valid int but out of range. `"²"` is a "digit" to `isdigit`, but `int` rejects it.
