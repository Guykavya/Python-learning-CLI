## Hint 1

How do you get the mean of a column for each of the two groups in pandas, and how do you take the difference "users minus others"? Which boolean column splits the rows?

## Hint 2

```text
u = df[df["app"]] ; o = df[~df["app"]]
return {"naive_diff": u["spend"].mean() - o["spend"].mean(), "engagement_gap": ..., "income_gap": ...}
```
