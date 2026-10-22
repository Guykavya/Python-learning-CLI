## Approach

The first `sum` uses up the generator: 0+1+4+9 = 14. After that it is exhausted: the second `sum` gives 0 and `list` gives `[]`. The list `squares2` is not consumed: both sums are 14. `bool(gen)` is `True` because generator objects have no length: even an exhausted generator is truthy. That is a classic trap.

## Output

```text
14
0
[]
14
14
True
[1, 2] True
```

## Complexity

O(n).

## Another way

Check for emptiness by trying `next(gen, None)` (careful if `None` may be a real item) or by converting to a list when it is small.
