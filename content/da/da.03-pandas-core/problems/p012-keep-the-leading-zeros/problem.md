# Keep the leading zeros

Chapter section 6.1. A postal code, a phone number or a product code is an **identifier**, not a number. If `read_csv`
guesses a number, `007` becomes `7` and the zeros are lost.

Write `read_with_codes(path)` that reads a CSV file with the columns `pin`, `product_code`, `qty` and returns a frame
where `pin` and `product_code` are text with every character kept (`"007"` stays `"007"`), while `qty` is still an
integer column (`int64`).

## Example

```text
pin,product_code,qty
007,00A1,3
012,0042,5
```

```python
df = read_with_codes("codes.csv")
df["pin"].tolist()            # ['007', '012']
df["product_code"].tolist()   # ['00A1', '0042']
df["qty"].tolist()            # [3, 5]
```
