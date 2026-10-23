## Hint 1

Run the tests. For `total_cost` and `price_label`, which exact value makes the code crash, and where did that value come from? What is the type of `find_price(menu, item)`?

## Hint 2

A value of type `float | None` must be narrowed before you add it or format it. Which check, and what should the function do on the `None` path: skip the item, or return the label `"n/a"`? For `cheapest_item`, what does the function return for an empty menu, and what must the hint then say?

## Hint 3

```
def total_cost(menu, order):
    total = 0.0
    for item in order:
        price = find_price(menu, item)
        if price is None: continue
        total += price
    return total

def cheapest_item(menu) -> str | None:   # same body

def price_label(menu, item):
    price = find_price(menu, item)
    if price is None: return "n/a"
    return "$" + format(price, ".2f")
```
