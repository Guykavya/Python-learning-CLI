## Hint 1

`itemgetter(1)` is a function: give it a tuple and it returns `t[1]`. `itemgetter("city", "age")` returns a
tuple of two values. How does `sorted` compare two tuples?

## Hint 2

`reduce(f, [a, b, c], start)` computes `f(f(f(start, a), b), c)`. What start value does not change a product?
For `largest`, which two values should `f` compare?

## Hint 3

```
sort_by_price: sorted(items, key=itemgetter(1))
product:       reduce(mul, nums, 1)
largest:       if empty: raise ValueError(...)
               reduce(lambda best, x: x if x > best else best, nums)
```
