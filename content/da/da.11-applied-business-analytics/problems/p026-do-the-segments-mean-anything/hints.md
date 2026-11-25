## Hint 1

Start from the customers (so those without later orders stay in), add their later spend and number of orders (0 where missing), then group by segment. Which sum divided by which count is "per customer"?

## Hint 2

```text
fut = orders_after.groupby("customer_id").agg(n=("amount","size"), spend=("amount","sum"))
t = rfm[["segment"]].join(fut).fillna({"n": 0, "spend": 0})
out = t.groupby("segment").agg(customers=("spend","size"), bought=("n", lambda s: (s>0).mean()*100), future=("spend","mean"))
```
