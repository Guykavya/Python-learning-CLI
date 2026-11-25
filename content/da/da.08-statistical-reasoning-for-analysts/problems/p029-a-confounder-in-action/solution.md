## Approach

Compute the three group differences. The naive difference mixes the effect of the app with the fact that app users are different people; the engagement and income gaps show how different.

## Code

```python
def confounder_report(df):
    users, others = df[df["app"]], df[~df["app"]]
    return {
        "naive_diff": float(users["spend"].mean() - others["spend"].mean()),
        "engagement_gap": float(users["engagement"].mean() - others["engagement"].mean()),
        "income_gap": float(users["income"].mean() - others["income"].mean()),
    }
```

## Complexity

O(n).

## Another way

`df.groupby("app")[["spend", "engagement", "income"]].mean().diff()` gives the same three numbers in one line. The next problems remove the confounding (stratification, regression).

## Pitfall to remember

The naive difference answers "how do app users compare with others?", not "what does the app do?".
