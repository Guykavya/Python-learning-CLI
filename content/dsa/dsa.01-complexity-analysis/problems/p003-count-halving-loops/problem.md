# Count the steps: halving and doubling

A loop that halves its variable each time is the source of every `log n` you will meet.
Predict **exactly** what this program prints. Do not run it.

```python
for n in [1, 2, 10, 64, 1000, 1000000]:
    halvings = 0
    m = n
    while m > 1:
        m = m // 2
        halvings += 1

    doublings = 0
    p = 1
    while p < n:
        p = p * 2
        doublings += 1

    print(n, halvings, doublings)
```

Write your answer in `answer.txt`, one line per printed line, three numbers separated by single spaces.

## Useful facts

- `2^10 = 1024`, so `2^20 = 1048576`, a little over a million.
- `m // 2` throws away the remainder: `7 // 2` is `3`.

## After you answer

Both counters are close to `log2(n)`. For which values of `n` are the two counters equal, and why?
