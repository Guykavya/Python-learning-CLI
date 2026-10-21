# Trace a nested loop

Predict **exactly** what this program prints. Do not run it. Work it out on paper first,
writing down the value of every variable each time the inner loop runs.

```python
total = 0
for i in range(1, 4):
    count = 0
    for j in range(i):
        count += 1
        total += i * j
        print(i, j)
    print("row", i, "count", count)
print("total", total)
```

Things to notice before you start:

- The inner loop's range depends on the outer variable `i`.
- `count` is reset to 0 at the start of every outer round, but `total` is not.
- `print(i, j)` puts a single space between the two values.

Write your answer in `answer.txt`, one line per printed line, exactly as Python would print it.
