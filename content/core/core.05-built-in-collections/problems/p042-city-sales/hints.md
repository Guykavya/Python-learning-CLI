## Hint 1

The outer dict maps a city to an inner dict. Use `setdefault(city, {})` to get the inner dict.

## Hint 2

`inner = sales.setdefault(city, {})` then `inner[item] = inner.get(item, 0) + qty`.

## Hint 3

A city's total is `sum(sales[city].values())`.
