## Approach

This is the *accumulator* pattern: start a total at 0, then add each number in turn.
`range(1, n + 1)` gives 1, 2, ..., n. When `n` is 0 the range is empty, the loop body never runs,
and the total stays 0, which is exactly right.

## Trace

Input `4`.

| Iteration | `i` | `total` after |
|---|---|---|
| 1 | 1 | 1 |
| 2 | 2 | 3 |
| 3 | 3 | 6 |
| 4 | 4 | 10 |

Output: `10`.

## Code

```python
n = int(input())
total = 0
for i in range(1, n + 1):
    total += i
print(total)
```

## Complexity

The loop runs `n` times: O(n). For `n = 1000000` that is a million additions, well under a second.

## Another way

There is a formula: `n * (n + 1) // 2`.

Write the sum forwards and backwards and add the two lines:

```
  1   +   2   + ... +   n
  n   + (n-1) + ... +   1
-------------------------
(n+1) + (n+1) + ... + (n+1)     (n times)
```

So twice the sum is `n * (n + 1)`, and the sum is half of that. This takes O(1) time no matter how big `n` is.
Use `//`, not `/`, so the answer stays an exact integer (with `/` you get a float like `15.0`, and for huge
`n` the float loses precision).

Prefer the formula when `n` can be enormous (say 10^18, where a loop would never finish). Prefer the loop
when you are summing something with no neat formula, which is most of the time.

## Edge cases

- `n = 0`: the range is empty and the answer is `0`.
- `n = 1`: answer `1`.
