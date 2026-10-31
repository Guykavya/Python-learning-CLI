## Hint 1

What does `combinations(items, 2)` give for three items? Does it ever pair an item with itself?
Does it give both `(a, b)` and `(b, a)`?

## Hint 2

Each pair is two tuples, like `(("pen", 20), ("mug", 30))`. How do you unpack the names and
the prices in the `for`?

## Hint 3

```
result = []
for (name1, price1), (name2, price2) in combinations(items, 2):
    if price1 + price2 == budget: append (name1, name2)
return result
```
