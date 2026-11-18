# Tribonacci with rolling variables

The Tribonacci numbers are like Fibonacci with three terms:

- `T(0) = 0`, `T(1) = 1`, `T(2) = 1`
- `T(n) = T(n - 1) + T(n - 2) + T(n - 3)` for `n >= 3`

Write `tribonacci(n)` that returns `T(n)` exactly (Python ints never overflow).

**Allowed memory:** `O(1)` extra space. Do **not** build a list of size `n`: each value only needs the three before it, so keep three variables and roll them forward (chapter section 6). The tests check the values and the running time; the memory rule is yours to keep, and it is the point of the exercise.

## Example

```python
>>> [tribonacci(n) for n in range(10)]
[0, 1, 1, 2, 4, 7, 13, 24, 44, 81]
>>> tribonacci(37)
2082876103
```

## Constraints

- `0 <= n <= 10**5`. `T(10**5)` has 87,914 bits (about 26,500 digits); the test prints it modulo `10**9 + 7` because Python refuses to turn an int with more than 4300 digits into a string.
- A recursion `n` deep fails; three recursive calls without a memo are hopeless already at `n = 40`.

## Think about

In `a, b, c = b, c, a + b + c`, which old values does the right-hand side use? Why does a version with three separate assignment lines go wrong?
