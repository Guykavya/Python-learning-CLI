# A confounder in action

Chapter section 8.3. In an observational dataset of customers, `app` tells whether the customer uses the shopping app, `spend` is monthly
spend, and `engagement` and `income` are standardised scores of how keen and how well-off the customer is. The **true** effect of the app
is +150 rupees in this simulated world, but we only see the table. Keen, well-off customers install the app more often.

Write `confounder_report(df)` returning a dict with three numbers (floats):

- `"naive_diff"`: mean `spend` of app users minus mean `spend` of the others;
- `"engagement_gap"`: mean `engagement` of app users minus mean `engagement` of the others;
- `"income_gap"`: the same for `income`.

The test builds the table with the chapter's generator (shown below), so you can try it yourself:

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

```python
world = make_app_world()
confounder_report(world)       # naive_diff is several times the true +150
```

## Example

If app users spend 2,930 on average and the others 2,280, `naive_diff` is 650. If app users average +0.6 engagement and the others -0.5,
`engagement_gap` is 1.1: the two groups are different people, not only different in app use.
