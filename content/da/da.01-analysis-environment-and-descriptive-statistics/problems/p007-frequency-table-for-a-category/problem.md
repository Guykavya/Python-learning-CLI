# Frequency table for a category

Chapter section 6.2: for a categorical column, the first summary is a **frequency table**: each value, how many times it occurs and what percent of all rows that is.

Write `frequency_table(values)` returning a list of `(value, count, percent)` tuples:

- `None` and the empty string `""` are **missing**: count them together under the label `"(missing)"` (they stay in the table, and in the total).
- sort by `count` **descending**, ties by `value` **ascending** (plain string order);
- `percent = 100 * count / total`, rounded to 1 decimal. An empty input gives `[]`.

## Example

```python
frequency_table(["bus", "car", "bus", None, "walk", "", "bus", "car"])
# [('bus', 3, 37.5), ('(missing)', 2, 25.0), ('car', 2, 25.0), ('walk', 1, 12.5)]
```

Note `"(missing)"` comes before `"car"`: equal counts are sorted by the value text.
