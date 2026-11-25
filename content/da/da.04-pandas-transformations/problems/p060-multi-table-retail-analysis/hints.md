## Hint 1

Build the working table once, step by step, before answering anything: lines → `+ orders` → `+ products` → `+ stores`
→ `+ returns`, each with `safe_merge(..., measure="revenue", ledger=ledger)`. After the returns join, which lines have a
missing `refund`, and what does that mean? Every question is then a `groupby` on this one table (or an anti-join with
`isin` for the unsold products and the inactive customers).

## Hint 2

```text
base = items.assign(revenue = qty * unit_price); total = base.revenue.sum()
f = safe_merge(base, orders, "order_id", ...) -> products[[product_id, category]] -> stores
    -> returns[[order_id, product_id, refund]] with validate="1:1"
returned = refund is present; refund = fillna(0); net = revenue * (1 - refund)
q1   = groupby([region, channel], as_index=False).agg(revenue sum, orders nunique)      reconcile with total
prod = groupby([category, product_id]).revenue.sum(); sort by category, -revenue, product_id
       rank = groupby(category).cumcount() + 1; keep rank <= 3
unsold = products not isin f.product_id; never = customers not isin orders.customer_id
month = order_date.dt.to_period("M"); revenue per month; compare with pd.period_range(min, max, freq="M")
        -> missing months -> ValueError; else mom_pct = pct_change() * 100;   reconcile with total
```
