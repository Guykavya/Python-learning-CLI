# Post-stratification weights

Chapter section 3. A survey over-represents one group (say Metro customers answered more often than Small-town ones). If you know the
true **population share** of each group, you can repair the estimate: take the mean inside each stratum of the sample and combine them
with the **population** shares instead of the sample shares.

Write `weighted_mean(sample_df, value, by, pop_shares)`:

- `sample_df` is a DataFrame, `value` the column to average, `by` the stratum column, `pop_shares` a dict `{stratum: share}`;
- result = the sum over strata of `share * (mean of value in that stratum)`;
- raise `ValueError` if a stratum of `pop_shares` has **no rows** in the sample (the message must contain its name);
- raise `ValueError` if a stratum of the sample is **missing from** `pop_shares` (message names it);
- raise `ValueError` if the shares do not add up to 1 (tolerance `1e-9`).

```python
df = pd.DataFrame({"city": ["Metro", "Metro", "Small", "Small", "Small"], "spend": [100, 120, 50, 70, 60]})
weighted_mean(df, "spend", "city", {"Metro": 0.3, "Small": 0.7})     # 0.3 * 110 + 0.7 * 60 = 75.0
```

## Example

The plain sample mean is 80 (Metro is 40% of the sample but only 30% of the population). The weighted mean is 75.
