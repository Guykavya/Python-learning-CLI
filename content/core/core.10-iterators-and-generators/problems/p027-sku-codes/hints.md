## Hint 1

`product(sizes, colours)` gives every pair `(size, colour)`. In which order does it give them?
Which loop stays on the same value longer?

## Hint 2

For each pair: skip it if it is in `unavailable`, otherwise build the code with an f-string and
upper-case it.

## Hint 3

```
for size, colour in product(sizes, colours):
    if (size, colour) in unavailable: continue
    yield f"{product_name}-{size}-{colour}".upper()
```
