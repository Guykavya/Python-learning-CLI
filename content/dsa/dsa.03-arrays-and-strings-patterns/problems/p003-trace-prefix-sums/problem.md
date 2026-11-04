# Trace prefix sums and range queries

This program builds a prefix sum list and then answers three range questions (1-based, inclusive).
Predict **exactly** what it prints. Do not run it.

```python
a = [3, -1, 4, 1, 5]
p = [0]
for x in a:
    p.append(p[-1] + x)
    print("add", x, "->", p[-1])
print("p =", p)
for l, r in [(1, 3), (2, 5), (4, 4)]:
    print(l, r, ":", p[r], "-", p[l - 1], "=", p[r] - p[l - 1])
print(len(a), len(p))
```

Write your answer in `answer.txt`, one line per printed line. Lines look like `add 3 -> 3` and `1 3 : 6 - 0 = 6`.

## How to work

Keep a row of boxes for `p`, starting with one box holding 0. For each `x`, write the new box: the last box plus `x`.
For each question, read box `r` and box `l - 1` (box numbers start at 0).

## After you answer

1. Check each answer by adding the elements directly: positions 2 to 5 are `-1 4 1 5`.
2. Why does the question `(4, 4)` give back exactly `a[3]`?
3. Why is `len(p)` one more than `len(a)`?
