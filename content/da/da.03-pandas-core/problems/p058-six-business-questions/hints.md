## Hint 1

Define "a sale" once: the rows where `returned` is `False`. Five of the six answers are about sales only; one (`returns_rate`) uses all rows. For each answer, which pandas tool of chapter 16 fits: `resample` for months, `value_counts` for counts and shares, `mean` of a boolean mask for a share?

## Hint 2

```text
sales = df[~df["returned"]]
revenue_by_month : revenue = qty*price where not returned else 0 -> set dates as index -> resample("MS").sum() -> index.strftime("%Y-%m")
top_products     : sales["product"].value_counts() -> sort by (-count, name) -> first n as (name, int(count))
channel_share    : sales["channel"].value_counts(normalize=True) -> dict
average_order_value : revenue of sales / len(sales)
repeat_customer_share : sales["customer"].value_counts() >= 2 -> .mean()
returns_rate     : df["returned"].mean()
```
`resample` fills the months in between, which gives the zero month for free.
