## Approach

Accumulator pattern with multiplication. Start `product` at 1, the "do nothing" value for multiplication,
and multiply it by 1, 2, ..., n. For `n = 0` the range is empty and the product stays 1, which matches `0! = 1`.

Python integers have no fixed size, so `300!` (615 digits) comes out exact.

## Trace

Input `5`.

| Iteration | `i` | `product` after |
|---|---|---|
| 1 | 1 | 1 |
| 2 | 2 | 2 |
| 3 | 3 | 6 |
| 4 | 4 | 24 |
| 5 | 5 | 120 |

Output: `120`.

## Code

```python
n = int(input())
product = 1
for i in range(1, n + 1):
    product *= i
print(product)
```

## Complexity

The loop does `n` multiplications: O(n) steps. (Strictly, each multiplication of huge numbers costs more than
one step, but for `n <= 300` it is instant.)

## Another way

Count down with a `while` loop:

```python
n = int(input())
product = 1
while n > 1:
    product *= n
    n -= 1
print(product)
```

Same result and same speed. Some people find counting down more natural because it matches how `n!` is
often written (`n * (n-1) * ... * 1`). In real code you would just use `math.factorial(n)`, which is faster
for very large `n`.

## Edge cases

- `0` and `1` both print `1`.
- Large `n`: the answer must be exact, so never use `/` or `float`.
