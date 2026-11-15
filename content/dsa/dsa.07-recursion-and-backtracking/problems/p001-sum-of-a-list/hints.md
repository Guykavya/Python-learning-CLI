## Hint 1

What is the sum of an empty list? That is your base case. For a non-empty list, how is its sum related to the sum of the list *without its first element*?

## Hint 2

Instead of slicing, carry an index `i`: "the sum of `xs[i:]`". When `i == len(xs)` nothing is left.

## Hint 3

```
def total(xs, i=0):
    if i == len(xs): return 0
    return xs[i] + total(xs, i + 1)
```
