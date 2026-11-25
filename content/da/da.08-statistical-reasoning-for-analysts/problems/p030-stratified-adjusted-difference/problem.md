# Stratified (adjusted) difference

Chapter section 8. To compare treated and untreated units **fairly**, compare them *inside* groups that are alike (strata), then combine
the within-group differences. Write `adjusted_diff(df, treat, outcome, by)`:

- `df` is a DataFrame, `treat` the name of a column with 0/1 or True/False, `outcome` a numeric column, `by` the stratum column;
- for each stratum with **at least one treated and one untreated row**, compute `mean(outcome | treated) - mean(outcome | untreated)`;
- combine with weights proportional to the **number of rows of each used stratum** (treated and untreated together);
- strata missing a treated or an untreated row are **skipped** (a within-stratum difference is undefined) and reported;
- return `(adjusted, skipped)`: a float and a **sorted list** of the skipped strata. If no stratum can be used, raise `ValueError`.

```python
df = pd.DataFrame({"g": ["mild"] * 4 + ["severe"] * 4, "t": [1, 0, 0, 0, 1, 1, 1, 0], "y": [80, 70, 70, 70, 50, 50, 50, 40]})
adjusted_diff(df, "t", "y", "g")        # (10.0, []): the naive difference is -5.0!
```

## Example

Treated patients are mostly severe cases, so their raw average (57.5) is *lower* than the untreated average (62.5): naive -5.
Inside each group the treatment helps by 10 (80 against 70; 50 against 40): the adjusted difference is +10. This is Simpson's paradox.
