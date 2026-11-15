# Flatten a nested list

Write `flatten(xs)` that takes a list whose items are either plain values or (nested) lists, and returns a **new** flat list with all plain values in the order they appear from left to right.

Only `list` objects are opened. Everything else (numbers, strings, tuples, `None`) is a plain value and is kept as one item, so `"ab"` stays `"ab"`.

## Example

```python
>>> flatten([1, [2, [3]], 4])
[1, 2, 3, 4]
>>> flatten([[], [[]], 5])
[5]
>>> flatten(["ab", ["c", (1, 2)]])
['ab', 'c', (1, 2)]
```

## Constraints

- The nesting depth is at most 50.
- Do not change `xs` or any inner list.

## Think about

What is the "smaller problem" here: a shorter list, or a less deeply nested one? You will probably need a loop over the items **and** a recursive call for each item that is a list.
