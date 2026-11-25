# Ticks, scales and limits

Chapter section 3. Three small settings decide whether an axis tells the truth: where it **starts**, how it is **scaled**, and how its
numbers are **written**.

Write `revenue_chart(df, log=False)`. `df` has a `month` column (timestamps) and a `revenue` column (numbers). Draw one line of revenue
against month and **return the Figure**.

- Linear chart (`log=False`): the y axis **starts at 0**.
- `log=True`: the y axis uses a **logarithmic** scale (a log axis cannot include 0, so do not force it).
- Both: y tick labels use a thousands separator, so a tick at 12000 reads `12,000`. Use `matplotlib.ticker.FuncFormatter`.
- Both: label the y axis `Revenue (USD)`.

```python
fig = revenue_chart(df)
fig.axes[0].yaxis.get_major_formatter()(12000, 0)    # '12,000'
```

## Example

For `log=False`, `ax.get_ylim()[0]` is `0.0` and `ax.get_yscale()` is `'linear'`. For `log=True`, `ax.get_yscale()` is `'log'`.
