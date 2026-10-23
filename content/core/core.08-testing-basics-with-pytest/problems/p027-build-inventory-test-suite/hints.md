## Hint 1

Make a checklist: for `add_item`: a new item, an existing item (adds up), name cleaning, bad quantity, empty name. For `remove_item`: some, all (item disappears), unknown item, too much, bad quantity. Then `total_items` and `low_stock`.

## Hint 2

Hunt for the quiet bugs: check the **dict afterwards**, not only the return value, check that a failing call leaves the stock unchanged, and use limits exactly equal to a quantity for `low_stock`.

## Hint 3

```
for each function: one normal test, one test per boundary, one test per raise (type AND message)
use stock = {} fresh in every test
parametrize the bad quantities and the bad names
after remove_item(all): assert name not in stock
after a failed remove: assert stock == original
```
