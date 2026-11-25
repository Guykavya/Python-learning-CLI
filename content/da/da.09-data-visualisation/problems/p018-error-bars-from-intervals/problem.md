# Error bars from intervals

Chapter section 4.8. A bar of two means invites the conclusion "A is higher than B". An **interval** shows how sure the mean is. The chapter's
function `mean_ci` returns the mean and the half-width of a 95% t interval (already in the starter; copy it, do not change it):

```python
def mean_ci(x, level=0.95):
    x = np.asarray(x, float)
    se = x.std(ddof=1) / np.sqrt(len(x))
    h = stats.t.ppf((1 + level) / 2, len(x) - 1) * se
    return x.mean(), h
```

Write `means_with_ci(df, group, value)`: one mean per group with its interval, drawn with **`ax.errorbar`** (not `ax.bar(yerr=...)`):

- groups in **sorted** order on the x axis; one point per group at its mean (`fmt="o"`, `capsize=5`);
- the **half-length of each error bar** equals `mean_ci`'s half-width for that group;
- the y axis starts at **0**;
- title contains `95% CI` (the reader must know what the whiskers are); y label is the name of `value`.

Return the Figure.

## Example

Group `a` has mean 10 and half-width 2: the dot is at 10 and the whisker runs from 8 to 12.
