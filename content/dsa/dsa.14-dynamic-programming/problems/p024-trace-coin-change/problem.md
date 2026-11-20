# Trace coin change

The fewest-coins table of chapter section 7, with the "last coin" pointers of section 9 and a print on every amount. Predict **exactly** what this program prints. Do not run it.

```python
INF = float("inf")
coins = [1, 3, 4]
amount = 6

f = [INF] * (amount + 1)
last = [None] * (amount + 1)
f[0] = 0
for a in range(1, amount + 1):
    tried = []
    for c in coins:
        if c <= a:
            tried.append(f[a - c] + 1)
            if f[a - c] + 1 < f[a]:
                f[a] = f[a - c] + 1
                last[a] = c
    print(f"a={a} tried={tried} f[a]={f[a]} last={last[a]}")
print("table:", f)

used = []
a = amount
while a > 0:
    used.append(last[a])
    a -= last[a]
print("coins used:", used)
print("answer:", f[amount])
```

Write your answer in `answer.txt`, one printed line per line: six `a=` lines, then the `table:`, `coins used:` and `answer:` lines.

## How to work

1. Draw a row of seven boxes, `f[0]` to `f[6]`, and a second row for `last`. Fill `f[0] = 0`; the rest are `INF` and `None`.
2. For each amount `a`, go through the coins **in the order 1, 3, 4**. Skip a coin bigger than `a`. For each other coin write `f[a - c] + 1` into the `tried` list (in that order).
3. `last[a]` changes only when a value is **strictly** smaller than the current `f[a]`. When two coins tie, which one stays?
4. The walk back starts at `a = 6`, appends `last[a]`, and subtracts it.

## After you answer

1. Greedy (dsa.13: always take the largest coin that fits) pays 6 with which coins? How many?
2. Which amount has a tie in its `tried` list for the minimum? Which coin ends up in `last` there, and why?
3. If the test were `<=` instead of `<`, which `last` values would change, and what would `coins used` be?
