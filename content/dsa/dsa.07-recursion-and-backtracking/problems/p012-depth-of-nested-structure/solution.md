## Approach

The depth of a list is one level for itself plus the depth of its deepest child list. A list without child lists has depth 1, which is the base case (the loop finds no list and `best` stays 0).

## Code

```python
def depth(xs):
    best = 0
    for item in xs:
        if isinstance(item, list):
            best = max(best, depth(item))
    return 1 + best
```

## Complexity

`O(total number of items)`: every list and value is visited once. The recursion depth equals the nesting depth.

## Another way

With a generator expression and the `default` argument of `max`:

```python
def depth(xs):
    return 1 + max((depth(x) for x in xs if isinstance(x, list)), default=0)
```
