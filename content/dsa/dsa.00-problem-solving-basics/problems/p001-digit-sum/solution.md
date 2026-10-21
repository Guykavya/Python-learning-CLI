## Approach

`n % 10` is the last digit. `n // 10` removes it. Repeat until `n` becomes 0.
Take `abs()` first, because `-905 % 10` is `5` in Python and `while n > 0` never runs for negatives.

## Code

```python
n = abs(int(input()))
total = 0
while n > 0:
    total += n % 10
    n //= 10
print(total)
```

## Complexity

The loop runs once per digit: O(d), where d is about log10(n).

## Edge cases

- `0`: the loop never runs and `total` stays 0, which is correct.
- Negative: handled by `abs()`.
