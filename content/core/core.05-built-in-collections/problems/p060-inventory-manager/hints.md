## Hint 1

Store each item as a dict entry: `qty[item]` and `price[item]` in two dicts, or one dict mapping
the item to a two-item list `[qty, price]`.

## Hint 2

For `low`, sort `(qty, name)` tuples. For `report`, sort `(-value, name)` tuples.

## Hint 3

Keep `revenue` as an int that grows with every successful sale.
