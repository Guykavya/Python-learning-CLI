# Count the steps: single loops

Before you can say "this is O(n)", you must be able to count how many times a line runs.
This program counts for you, using a counter in each loop. Predict **exactly** what it prints.
Do not run it.

```python
n = 20

a = 0
for i in range(n):
    a += 1

b = 0
for i in range(0, n, 3):
    b += 1

c = 0
for i in range(5, n + 1):
    c += 1

d = 0
i = 1
while i <= n:
    d += 1
    i += 2

e = 0
for i in range(n):
    if i % 4 == 0:
        e += 1
    e += 1

print("a", a)
print("b", b)
print("c", c)
print("d", d)
print("e", e)
```

Write your answer in `answer.txt`, one line per printed line, for example `a 7`.

## Example of the method

For `for i in range(2, 9, 2)`, the values are 2, 4, 6, 8, so the body runs 4 times.
A quick formula for `range(start, stop, step)` with a positive step is
`(stop - start + step - 1) // step` when `stop > start`, and 0 otherwise.

## After you answer

For each counter, write a formula in terms of a general `n` (not just 20). For example, `a` is `n`.
Which counters grow like `n`? Is any of them not proportional to `n`?
