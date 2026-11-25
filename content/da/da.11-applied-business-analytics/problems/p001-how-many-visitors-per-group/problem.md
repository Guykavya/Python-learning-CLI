# How many visitors per group?

Chapter section 2.2. Before you start an experiment you decide **how many visitors each group needs**, otherwise the test cannot answer the question. For a conversion rate `p0` in the control
group, a smallest lift worth detecting `mde` (in absolute terms, 0.005 = half a percentage point), a significance level `alpha` and a power, the chapter uses

```text
z_a = z-value for 1 - alpha/2          z_b = z-value for the power
p1 = p0 + mde            p_bar = (p0 + p1) / 2
n = 2 * (z_a + z_b)^2 * p_bar * (1 - p_bar) / mde^2          (rounded UP to a whole visitor)
```

Write `n_per_group(p0, mde, alpha=0.05, power=0.80)` that returns `n` as a plain `int`. Use `scipy.stats.norm.ppf` for the z-values.

- Always round **up** (`math.ceil` or `np.ceil`): 99.1 visitors means 100.
- If `mde <= 0`, or `p0 + mde >= 1`, or `p0 <= 0`, raise `ValueError("need 0 < p0 and 0 < mde and p0 + mde < 1")`.

## Example

```python
n_per_group(0.06, 0.005)       # 36792 visitors per group to detect +0.5 points from 6%
```
