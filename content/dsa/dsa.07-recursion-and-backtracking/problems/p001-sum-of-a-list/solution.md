## Approach

The sum of `xs[i:]` is `xs[i]` plus the sum of `xs[i+1:]`. The empty tail (`i == len(xs)`) has sum 0. Passing the index `i` instead of a slice avoids copying the list.

## Code

```python
def total(xs, i=0):
    if i == len(xs):          # base case: nothing left
        return 0
    return xs[i] + total(xs, i + 1)
```

## Complexity

`O(n)` time and `O(n)` stack depth (one frame per element). The slicing version `xs[0] + total(xs[1:])` is `O(n^2)` time because every slice copies the rest.

## Another way

The slicing version is shorter and fine for small lists:

```python
def total(xs):
    if not xs:
        return 0
    return xs[0] + total(xs[1:])
```

In real code you would write `sum(xs)`: recursion over a long list hits the recursion limit at about 1000 items.
