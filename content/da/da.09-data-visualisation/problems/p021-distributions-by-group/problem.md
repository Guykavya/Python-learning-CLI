# Distributions by group

Chapter section 5.2. Two groups of different sizes are hard to compare with histograms of **counts**: the bigger group always looks taller. Comparing
**shapes** needs a **density** scale, with each group normalised on its own.

Write `hist_by_group(df)`. `df` has the columns `value` (numbers) and `group` (text). Draw one histogram of `value` with seaborn's `histplot`:

- one histogram per `group` (the `hue` argument);
- `stat="density"` and `common_norm=False`, so that **each group's bar areas add up to 1**;
- a legend whose entries are the group names.

Return the Figure.

```python
fig = hist_by_group(df)
```

## Example

300 values in group `a` and 100 in group `b`: with these settings both groups have total area 1, although `a` has three times as many rows.
