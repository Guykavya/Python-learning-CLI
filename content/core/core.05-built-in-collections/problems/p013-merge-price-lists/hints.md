## Hint 1

Turn each line into a dict. For each pair, `name, price = pair.split("=")`.

## Hint 2

`merged = old | new` makes a new dict where the right side wins. Then loop over `sorted(merged)`.

## Hint 3

An item changed if `item in old and item in new and old[item] != new[item]`. Collect those with a
comprehension over `new`, then sort.
