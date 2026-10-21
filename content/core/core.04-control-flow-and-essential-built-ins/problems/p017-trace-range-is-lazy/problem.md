# Trace range as a lazy sequence

A `range` stores only `start`, `stop` and `step`, and computes everything else. Predict
**exactly** what this program prints. Do not run it.

```python
r = range(3, 30, 4)
print(r)
print(len(r), r[0], r[-1], r[2])
print(15 in r, 16 in r, 31 in r)
print(r[1:4])
print(list(r[1:4]))
print(range(0, 10, 3)[-1])
big = range(0, 10**12, 5)
print(len(big))
print(big[10**11])
print(999_999_999_995 in big)
print(list(reversed(range(1, 8, 3))))
e = range(10, 0)
print(len(e), bool(e), bool(range(1)))
print(range(0, 6, 2) == range(0, 5, 2))
```

Two things not shown directly in the chapter: slicing a range gives another range, and two
ranges are equal (`==`) when they produce the same numbers.

Write your answer in `answer.txt`, one printed line per line.
