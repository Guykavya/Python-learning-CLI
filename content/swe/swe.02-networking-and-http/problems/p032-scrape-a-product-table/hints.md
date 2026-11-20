## Hint 1

Which CSS selector picks the rows? `soup.select("tr.product")` returns a list of tags. Inside a row, `row.select_one("td.name")` finds the cell or returns `None`.

## Hint 2

`cell.get_text()` returns all text below the tag, nested tags included. `" ".join(text.split())` collapses every run of white space. For the price, search the text for a number with a regular expression and remove the commas before `Decimal(...)`.

## Hint 3

```text
for row in soup.select("tr.product"):
    name_cell = row.select_one("td.name"); skip the row if None
    price: m = re.search(r"\d[\d,]*(?:\.\d+)?", cell text); None if no match; Decimal(m.group().replace(",", ""))
    stock: text = " ".join(cell text .split()).lower(); in_stock = text.startswith("in stock")
```
