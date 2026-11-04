# Trace the extended Euclid table

This is the loop version of extended Euclid. Each pass prints a row `q r s t`. Every remainder `r` is kept as a combination
`r = a*s + b*t`. Predict **exactly** what the program prints. Do not run it.

```python
def table(a, b):
    r0, r1 = a, b
    s0, s1 = 1, 0
    t0, t1 = 0, 1
    print("q r s t")
    print("-", r0, s0, t0)
    print("-", r1, s1, t1)
    while r1 != 0:
        q = r0 // r1
        r0, r1 = r1, r0 - q * r1
        s0, s1 = s1, s0 - q * s1
        t0, t1 = t1, t0 - q * t1
        print(q, r1, s1, t1)
    print("gcd", r0, "x", s0, "y", t0)
    print("check", a * s0 + b * t0)


table(240, 46)
print("---")
table(99, 78)
print("---")
table(17, 0)
```

Write your answer in `answer.txt`, one line per printed line (including the `---` separators and the header `q r s t`).

## How to work

Keep four columns. The two starting rows are `(a, 1, 0)` and `(b, 0, 1)`: `a = a*1 + b*0`, `b = a*0 + b*1`. Each new
row is **row0 - q * row1**, applied to `r`, `s` and `t` together. After the shift, `row0` is the old `row1`.

## After you answer

1. In every row, check that `240*s + 46*t = r`. Does it hold? Why must it?
2. The program prints `s0` and `t0` at the end, not `s1` and `t1`. Which row do they come from, and why is it not the last
   printed row?
3. For `table(17, 0)` the loop does not run. What are `gcd`, `x`, `y`?
