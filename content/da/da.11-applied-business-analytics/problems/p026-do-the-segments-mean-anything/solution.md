## Approach

The `join` keeps every customer of `rfm`; filling the missing later spend with 0 makes "per customer" mean "per customer **in the segment**", which is what a campaign planner needs. The ranking of the segments by future spend is the test of whether they mean anything.

## Code

```python
import pandas as pd


def future_value_by_segment(rfm, orders_after):
    fut = orders_after.groupby("customer_id").agg(n=("amount", "size"), spend=("amount", "sum"))
    t = rfm[["segment"]].join(fut).fillna({"n": 0, "spend": 0})
    out = t.groupby("segment").agg(customers=("spend", "size"),
                                   bought_again_pct=("n", lambda s: float((s > 0).mean() * 100)),
                                   future_spend_per_customer=("spend", "mean"))
    out["customers"] = out["customers"].astype(int)
    return out.sort_values("future_spend_per_customer", ascending=False)
```

## Complexity

O(n).

## Another way

Rank all customers by their RFM score at `T` and compare the share of **future revenue** captured by the top 20% with the 20% a random pick would capture: a single number for how well the whole scheme predicts.
