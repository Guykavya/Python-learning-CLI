# Scrape a product table

Chapter section 23. A shop page lists products in a table:

```html
<table id="products">
  <tr><th>Name</th><th>Price</th><th>Stock</th></tr>
  <tr class="product">
    <td class="name">  Green <a href="/t/1"><b>Tea</b></a>  </td>
    <td class="price">₹1,299.00</td>
    <td class="stock">In stock</td>
  </tr>
</table>
```

Write `parse_products(html)` using **BeautifulSoup** (`html.parser`). Return a list of dicts, one per `<tr class="product">`, in page order:

```python
{"name": "Green Tea", "price": Decimal("1299.00"), "in_stock": True}
```

- `name`: the **text** of the `td.name` cell, with nested tags removed and every run of white space (spaces, newlines) collapsed to one space, trimmed. A product row with no `td.name` is skipped.
- `price`: a `Decimal` made from the number in the `td.price` cell: ignore the currency sign (`₹`, `Rs.`, `$`), spaces and thousands commas (`"₹1,299.00"` becomes `Decimal("1299.00")`). If the cell is missing, empty, or has no number (`"N/A"`, `"Ask us"`), the price is `None`. **Never raise** for a bad price.
- `in_stock`: `True` when the text of `td.stock` (case-insensitive, white space collapsed) **starts with** `in stock`; `False` for `Out of stock`, anything else, or a missing cell.
- Rows without the class `product` (for example the header row) are ignored. A page with no products gives `[]`.

## Example

```python
parse_products(html)
# [{"name": "Green Tea", "price": Decimal("1299.00"), "in_stock": True}]
```
