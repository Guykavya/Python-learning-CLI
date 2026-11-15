# Binary strings of length n

Write `binary_strings(n)` that returns a list of all strings of length `n` made of the characters `"0"` and `"1"`, in **lexicographic** (dictionary) order. This is the simplest backtracking problem in the chapter (section 5): at each position choose `"0"` or `"1"`.

For `n = 0` the answer is `[""]`: there is exactly one string of length 0, the empty one.

## Example

```python
>>> binary_strings(2)
['00', '01', '10', '11']
>>> binary_strings(0)
['']
```

## Constraints

- `0 <= n <= 14`
- Write the recursion yourself; `itertools.product` and `format(x, "b")` are not allowed.

## Think about

In which order must the loop try the two characters so that the result comes out sorted without calling `sort`?
