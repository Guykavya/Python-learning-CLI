## Approach

The last binary digit decides odd or even, exactly like the last decimal digit decides
divisibility by 10. `n & 1` isolates that bit.

## Code

```python
n = int(input())
print((n & 1) == 1)
print(n >> 1)
print(n << 1)
```

## Why it works for negatives

Python treats negative ints as if they had an infinite row of 1 bits on the left (two's
complement). `-7` ends in binary `...1001`, so its last bit is 1 and it is odd.
`-7 >> 1` is `-4`, the same as `-7 // 2`: shifting right is floor division by 2.

## Another way

`bool(n & 1)` also gives `True` or `False`, because `1` is truthy and `0` is falsy.
