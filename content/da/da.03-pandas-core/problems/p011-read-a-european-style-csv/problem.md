# Read a European-style CSV

Chapter section 6.1. A supplier sends a file made in a country where `;` separates fields, `,` is the decimal mark, `.`
separates thousands and `-` means "no value". The dates are `day.month.year`.

```text
order_id;date;customer;qty;price
1;05.03.2024;Asha;2;1.250,50
2;06.03.2024;Ben;-;9,5
3;31.03.2024;Chen;4;-
```

Write `read_shop_csv(path)` that reads such a file and returns a DataFrame where:

- `order_id` is `int64`, `customer` is text;
- `date` is a datetime column (`05.03.2024` is 5 March);
- `qty` and `price` are `float64`; `1.250,50` is `1250.5`, and a `-` is `NaN`.

Use the arguments of `pd.read_csv`; do not convert the columns by hand afterwards.

## Example

```python
df = read_shop_csv("shop.csv")
df["price"].tolist()          # [1250.5, 9.5, nan]
df["qty"].tolist()            # [2.0, nan, 4.0]
df["date"].iloc[0]            # Timestamp('2024-03-05 00:00:00')
```
