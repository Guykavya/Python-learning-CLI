# Count the steps: nested loops

The program below counts how many times the innermost line of four different nested loops runs,
first for `n = 6` and then for `n = 1000`. Predict **exactly** what it prints. Do not run it.

```python
for n in [6, 1000]:
    a = 0
    for i in range(n):
        for j in range(n):
            a += 1

    b = 0
    for i in range(n):
        for j in range(i):
            b += 1

    c = 0
    for i in range(n):
        for j in range(i, n):
            c += 1

    d = 0
    for i in range(n):
        for j in range(3):
            d += 1

    print(n, a, b, c, d)
```

Write your answer in `answer.txt`: two lines, each with five numbers separated by single spaces.

You can trace the `n = 6` case with a table. You cannot trace `n = 1000` by hand: you need a formula.
Find the formula from the small case, then use it.

## Example

For `for i in range(4): for j in range(i):`, the inner loop runs 0, 1, 2, 3 times, a total of 6.
