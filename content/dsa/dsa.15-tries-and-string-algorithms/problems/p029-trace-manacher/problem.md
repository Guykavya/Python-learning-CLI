# Trace Manacher

Manacher's algorithm (chapter section 15) on `abaxaba`, with a print per position: `i`, the character `t[i]`, the radius copied from the mirror (`start`), the final radius `p[i]`, and the rightmost palindrome `(c, r)` after the step. Predict **exactly** what this program prints. Do not run it.

```python
s = "abaxaba"
t = "#" + "#".join(s) + "#"
n = len(t)
p = [0] * n
c = r = 0
for i in range(n):
    mirror = 2 * c - i
    start = min(r - i, p[mirror]) if i < r else 0
    p[i] = start
    while i - p[i] - 1 >= 0 and i + p[i] + 1 < n and t[i - p[i] - 1] == t[i + p[i] + 1]:
        p[i] += 1
    if i + p[i] > r:
        c, r = i, i + p[i]
    print(i, t[i], start, p[i], c, r)
print(p)
```

Write your answer in `answer.txt`, one printed line per line: 15 lines for `i = 0` to `14`, then the list `p`.

## How to work

1. Write `t = #a#b#a#x#a#b#a#` with its indices 0 to 14.
2. For each `i`: if `i < r`, the start is `min(r - i, p[2c - i])` (read `p` of the mirror from what you already wrote); otherwise 0.
3. Expand: compare `t[i - p - 1]` with `t[i + p + 1]` while both are inside `t`; each match adds 1.
4. If `i + p[i] > r`, the new `(c, r)` is `(i, i + p[i])`.

## After you answer

1. Which rows got a positive `start` from their mirror? For which of them did the expansion add nothing?
2. Row `i = 11` starts at 3 and stops at once. Why can it not grow, although the mirror of `11` around `c = 7` grew no further either?
3. What is the longest palindrome of `abaxaba`, and how do you read it from `p`?
