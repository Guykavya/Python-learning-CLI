# Welch t-test by hand

Chapter section 14.3. **Welch's t-test** compares the means of two groups without assuming equal variances:

- `t = (mean_a - mean_b) / sqrt(va / na + vb / nb)` with `va`, `vb` the sample variances (`ddof=1`);
- degrees of freedom (Welch-Satterthwaite): `df = (va/na + vb/nb)^2 / ((va/na)^2 / (na - 1) + (vb/nb)^2 / (nb - 1))`;
- two-sided p-value: `2 * P(T > |t|)`.

Write `welch_t(a, b, t_sf)` returning `(t, df, p)`. `t_sf(x, df)` is the **survival function** of the t-distribution `P(T > x)` and is **passed in**.

## Example

```text
a = [5.1, 4.9, 5.3, 5.0]   b = [4.2, 4.4, 4.0, 4.5]    ->  t about 5.72, p about 0.0015
```
