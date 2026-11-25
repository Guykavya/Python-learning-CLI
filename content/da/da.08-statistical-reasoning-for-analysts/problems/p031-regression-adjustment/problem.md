# Regression adjustment

Chapter section 8.3. When there are several confounders (or continuous ones), put them in a **regression** next to the treatment: the
coefficient of the treatment is then the difference in the outcome **holding the other variables fixed**.

Write `adjusted_effect(df)` for a table with columns `app` (bool), `engagement`, `income`, `spend` (the world of problem 29):

- fit `spend ~ app_i + engagement + income` by ordinary least squares with `statsmodels.formula.api.ols`, where `app_i` is the
  `app` column converted to 0/1 integers (add it to a copy of the table);
- return a tuple `(coef, ci_low, ci_high)` for the `app_i` coefficient: the estimate and its 95% confidence interval (`fit.conf_int()`).

A formula needs numbers, so convert the Boolean first:

```python
import statsmodels.formula.api as smf
fit = smf.ols("spend ~ app_i + engagement + income", data=df.assign(app_i=df["app"].astype(int))).fit()
```

The generator is the same as in problem 29:

```python
def make_app_world(n=4000, tau=150, seed=60):
    rng = np.random.default_rng(seed)
    engagement = rng.normal(0, 1, n)
    income = rng.normal(0, 1, n)
    p_app = 1 / (1 + np.exp(-(-0.3 + 1.2 * engagement + 0.6 * income)))      # keen, well-off customers install the app
    app = rng.random(n) < p_app
    spend = 2500 + 400 * engagement + 300 * income + tau * app + rng.normal(0, 500, n)
    return pd.DataFrame({"engagement": engagement, "income": income, "app": app, "spend": spend})
```

## Example

On `make_app_world(n=4000)` the naive difference is about 650, but the adjusted coefficient is close to the true 150 (the interval
is roughly 30 rupees on each side).
