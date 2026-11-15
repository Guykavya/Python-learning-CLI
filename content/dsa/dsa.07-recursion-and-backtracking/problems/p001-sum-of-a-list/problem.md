# Sum of a list, recursively

Write `total(xs)` that returns the sum of the numbers in the list `xs`, **using recursion**.
No `for` or `while` loop, no comprehension, and no built-in `sum`: the point is to practise the two parts of every recursive function (chapter section 2):

- the **base case**: the smallest list, whose answer you know without any work;
- the **recursive step**: one element plus the answer for a smaller list.

The empty list has sum `0`.

## Example

```python
>>> total([3, 1, 4, 1, 5])
14
>>> total([])
0
>>> total([-2, 2.5])
0.5
```

## Constraints

- `0 <= len(xs) <= 900` (the tests stay below Python's recursion limit of about 1000 calls).
- The items are `int` or `float`.
- Do not change `xs`.

## Think about

`nums[1:]` copies the rest of the list at every call. The chapter shows a version that passes an **index** instead. Both pass the tests here; which one is `O(n)`?
