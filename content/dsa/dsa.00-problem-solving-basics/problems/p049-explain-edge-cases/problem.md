# Explain: finding the edge cases

Here is a small problem:

> Read `n`, then `n` integers, one per line. Print the average (with 2 decimal places), the
> largest value and the smallest value.

A typical first attempt looks like this:

```python
n = int(input())
total = 0
largest = 0
smallest = 0
for i in range(n):
    x = int(input())
    total += x
    if x > largest:
        largest = x
    if x < smallest:
        smallest = x
print(f"{total / n:.2f}")
print(largest)
print(smallest)
```

It works for `3`, `4`, `9`, `-2`. It is still wrong. Answer in `answer.md`:

1. List **at least 6** edge-case inputs for this problem. Include at least: `n = 0`, `n = 1`,
   all values negative, all values equal, very large values, and a negative `n`. For each, write
   the correct expected output or what the program *should* do (you decide a sensible rule where
   the problem statement is silent, and say so).
2. Which of your edge cases break the attempt above, and exactly how (crash? wrong number? which one)?
3. In general, how do you choose test inputs for a problem you have never seen? Explain boundaries,
   the smallest and largest allowed values, and "just inside / just outside" a limit.
4. Write a short checklist (5 to 8 items) you will reuse before calling any solution finished.

Write in your own words. Use concrete numbers in your examples.
