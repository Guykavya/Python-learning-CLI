# Trace a fixed sliding window

This program finds the largest sum of a window of 3 neighbouring elements. At every slide it prints the element that
enters, the element that leaves, the new window, its sum and the best sum so far. Predict **exactly** what it prints.
Do not run it.

```python
a = [4, 2, -1, 3, 5, -6, 1]
k = 3
s = sum(a[:k])
best = s
print("start", a[:k], s)
for r in range(k, len(a)):
    add = a[r]
    remove = a[r - k]
    s = s + add - remove
    if s > best:
        best = s
    print("add", add, "remove", remove, "window", a[r - k + 1:r + 1], "sum", s, "best", best)
print("best", best)
```

Write your answer in `answer.txt`, one line per printed line. Lines look like
`add 3 remove 4 window [2, -1, 3] sum 4 best 5`.

## How to work

Write the array with indices `0..6` under it. For each `r` from 3 to 6, circle `a[r]` (enters) and cross out
`a[r - 3]` (leaves). Update the sum with those two numbers only; then check it by adding the window directly.

## After you answer

1. How many lines start with `add`? How many windows of size 3 does an array of 7 elements have?
2. Subtracting a negative number: what happens to the sum when `-1` leaves?
3. Which window has the best sum, and is it the last one?
