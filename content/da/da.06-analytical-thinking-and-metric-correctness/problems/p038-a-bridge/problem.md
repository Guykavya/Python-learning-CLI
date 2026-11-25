# A bridge

Chapter section 11.4. A **bridge** (or waterfall) lists the starting number, each effect with its sign, and the
ending number. The effects must add up exactly to the difference. It is the standard form of a reconciliation report.

Write `bridge(start_label, start_value, steps, end_label, end_value)`.

- `steps` is a list of `(label, change)` pairs, `change` an integer with its sign.
- Return a **text table** (one string, lines joined with `"\n"`, no newline at the end, every line **right-stripped**
  of trailing spaces). The columns are joined with `" | "`:
  1. header line: `step | change | running | check`
  2. the start line: `<start_label> |  | <start_value> |` (the change and check cells are empty, so there are two spaces between the bars)
  3. one line per step: `<label> | <change with sign, e.g. -20 or +29> | <running total> |`
  4. the end line: `= <end_label> |  | <end_value> | OK`
- The running total starts at `start_value` and adds each change in order.
- If the final running total is **not** equal to `end_value`, do not return a table: raise `ValueError` with the text
  `"UNEXPLAINED <gap>: bridge from <start_label> does not reach <end_label>"`, where `<gap>` is
  `running total - end_value` written with a sign (`+3`, `-5`).

Build each line by joining its four cells with `" | "` (an empty cell is an empty text) and then calling `.rstrip()`,
which removes the space left after the last bar when the `check` cell is empty.

## Example

```python
steps = [("ops only: completed in Feb, paid later", -20), ("finance only: paid in Feb, completed in Jan", +29)]
print(bridge("jobs completed in Feb", 807, steps, "jobs paid in Feb", 816))
```

```text
step | change | running | check
jobs completed in Feb |  | 807 |
ops only: completed in Feb, paid later | -20 | 787 |
finance only: paid in Feb, completed in Jan | +29 | 816 |
= jobs paid in Feb |  | 816 | OK
```
