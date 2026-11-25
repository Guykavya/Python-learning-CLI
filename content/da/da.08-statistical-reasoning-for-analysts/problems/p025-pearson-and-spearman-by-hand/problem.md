# Pearson and Spearman by hand

Chapter section 7. **Pearson's r** measures how closely two variables follow a straight line:
`r = sum((x - mean_x)(y - mean_y)) / sqrt(sum((x - mean_x)^2) * sum((y - mean_y)^2))`.
**Spearman's rho** is Pearson's r computed on the **ranks** (ties get the average of the ranks they share, `scipy.stats.rankdata`),
so it measures how well one variable *increases with* the other, in any shape.

Write `pearson(x, y)` and `spearman(x, y)` **without** calling `scipy.stats.pearsonr/spearmanr` or `np.corrcoef` (you may use
`scipy.stats.rankdata` and NumPy arithmetic). Raise `ValueError` when the lengths differ, when there are fewer than 2 points, or when
a variable is constant, with the message `r is undefined when one variable does not vary`.

```python
pearson([1, 2, 3, 4, 5], [2, 4, 6, 8, 40])     # 0.8
spearman([1, 2, 3, 4, 5], [2, 4, 6, 8, 40])    # 1.0: the order is perfectly preserved
```

## Example

`spearman([1, 2, 2, 3], [10, 20, 20, 30])` ranks the ties as 2.5 each and gives 1.0.
