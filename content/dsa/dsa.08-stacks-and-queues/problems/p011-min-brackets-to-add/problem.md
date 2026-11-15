# Minimum brackets to add

`s` contains only `(` and `)`. Write `brackets_to_add(s)` that returns a tuple `(opens, closes)`: the smallest number of `(` and the smallest number of `)` you must **insert** (anywhere) to make `s` balanced.

There are two kinds of imbalance:

- a `)` that arrives when nothing is open needs an extra `(` somewhere **before** it;
- a `(` that is still open at the end needs an extra `)` somewhere **after** it.

With only one kind of bracket you do not need a stack: a counter of "open so far" is enough (chapter section 5, variant 1).

## Example

```python
>>> brackets_to_add("())")
(1, 0)
>>> brackets_to_add("(((")
(0, 3)
>>> brackets_to_add("()))((")
(2, 2)
>>> brackets_to_add(")(")
(1, 1)
>>> brackets_to_add("")
(0, 0)
```

`"()))(("`: the first pair is fine, the next two `)` have nothing to close (add two `(`), and the last two `(` are never closed (add two `)`).

## Constraints

- `0 <= len(s) <= 10**5`.

## Think about

`")("` has one of each bracket, so the counts are equal, yet you must add 2 brackets. Why is "count `(` minus count `)`" not enough?
