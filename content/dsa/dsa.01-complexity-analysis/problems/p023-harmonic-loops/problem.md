# The loop with a growing step

The inner loop below starts at `i` and jumps by `i`: it visits `i, 2i, 3i, ...` up to `n`. So it runs many times
when `i` is small and few times when `i` is large. Predict **exactly** what the program prints. Do not run it.

```python
for n in [1, 6, 12, 30]:
    count = 0
    for i in range(1, n + 1):
        for j in range(i, n + 1, i):
            count += 1
    print(n, count)
```

Write your answer in `answer.txt`, one line per printed line, two numbers separated by a single space.

## After you answer

1. How many times does the inner loop run for a given `i`? Write the count as a formula.
2. Another way to read `count`: for each `j`, how many `i` reach it? (Hint: `i` must divide `j`.)
3. Is this O(n^2)? Estimate the total for `n = 10^6` (use the fact that `1 + 1/2 + 1/3 + ... + 1/n` is about
   `ln(n) + 0.58`).
