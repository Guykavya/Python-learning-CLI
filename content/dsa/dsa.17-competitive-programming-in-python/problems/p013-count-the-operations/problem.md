# Count the operations

The rule of this course: CPython does about `10**7` simple operations per second, and the time limit is **2 seconds**. So a program passes (`OK`) when it does **at most `2 * 10**7`** simple operations, and gets `TLE` (time limit exceeded) when it does more. One "operation" is one pass through the body of the innermost loop.

For each of the six programs below, decide `OK` or `TLE`. Count the passes through the innermost body: do the arithmetic by hand, do not run the code.

```python
# 1
n = 150
for i in range(n):
    for j in range(n):
        for k in range(n):
            pass

# 2
n = 10**5
for i in range(n):
    for j in range(n):
        pass

# 3
n = 10**5
for i in range(n):
    j = 1
    while j < n:
        j *= 2

# 4
n = 20000
for i in range(n):
    for j in range(i, n):
        pass

# 5   (a sieve)
n = 10**6
comp = [False] * n
for i in range(2, n):
    if not comp[i]:
        for j in range(i * i, n, i):
            comp[j] = True

# 6
n = 3 * 10**6
for i in range(1, n + 1):
    for j in range(i, n + 1, i):
        pass
```

Write your answer in `answer.txt`, one line per program, in the form `1: OK` or `2: TLE`.

## How to work

1. For each program write a formula for the number of body executions (`n * n * n`, `n * n`, `n * log2 n`, ...).
2. Put in the number and compare with `2 * 10**7`.
3. Use rough values: `log2(10**5)` is about 17, `ln(3 * 10**6)` is about 15, a sieve does about `n * ln(ln n)` inner steps.

## After you answer

1. Which program has the smallest count, and which the largest?
2. For program 3, how many times does the `while` body run for **one** `i`?
3. For program 6, why is the count roughly `n * ln n` and not `n * n`?
