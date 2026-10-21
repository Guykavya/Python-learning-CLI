## Approach

Keep two variables, `largest` and `smallest`, holding the best values seen so far. Each new number is compared
with both and replaces them if it beats them.

The key decision is the starting values. Starting `largest` at 0 is a classic bug: if every number is negative,
nothing ever beats 0 and the program prints `max 0`, a number that was never in the input. The safe start is
the first number itself: it is a real input value, so it is a correct "best so far" after one number.

Use two separate `if`s, not `if / elif`. A single number can update both (the first number does, in the other
style below).

## Trace

Input `4`, then `3 -1 9 2`. The first number, 3, sets both variables.

| Step | `x` | `largest` after | `smallest` after |
|---|---|---|---|
| start | 3 | 3 | 3 |
| 1 | -1 | 3 | -1 |
| 2 | 9 | 9 | -1 |
| 3 | 2 | 9 | -1 |

Output: `max 9` then `min -1`.

## Code

```python
n = int(input())
x = int(input())
largest = x
smallest = x
for _ in range(n - 1):
    x = int(input())
    if x > largest:
        largest = x
    if x < smallest:
        smallest = x
print("max", largest)
print("min", smallest)
```

## Complexity

One pass over the numbers: O(n) time, and only two variables of memory, O(1), no matter how many numbers arrive.

## Another way

Start with values that any real input will beat: `largest = float("-inf")` and `smallest = float("inf")`,
then loop over all `n` numbers. The first comparison always replaces them. This avoids reading the first
number separately, and it is handy when the loop is more complicated. The cost is mixing a float into
integer code; it works in Python, but the "first element" start is cleaner and works in every language.

You could also call `max(largest, x)` and `min(smallest, x)` inside the loop instead of the two `if`s.

## Edge cases

- `n = 1`: the loop runs zero times and the one number is both max and min.
- All negative: handled because the start is a real input value.
- The first number is the largest, or the last is the smallest: the comparisons must run for every number.
