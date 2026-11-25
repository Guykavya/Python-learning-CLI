## Hint 1

Write the rule as a sentence with brackets: NOT cancelled AND (local-and-big OR rush). Which Python operators are `AND`, `OR`, `NOT` for Series? Which parts need their own parentheses because `&` binds tighter than `>` and `==`?

## Hint 2

```text
local_big = (df["city"] == city) & (df["amount"] >= min_amount)
keep      = (local_big | df["rush"]) & ~(df["status"] == "cancelled")
return df[keep]
```
