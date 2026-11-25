# Residual sum of squares for three lines

Chapter section 3.2. The **residual sum of squares** (RSS) of a line is the sum of the squared vertical gaps between the points and the line. Least squares picks the line with the smallest RSS.

```python
points = [(1, 2), (2, 3), (3, 5), (4, 6)]
lines = [(0.0, 2.0), (0.5, 1.4), (1.0, 1.0)]   # (intercept b0, slope b1)


def rss(b0, b1):
    return sum((y - (b0 + b1 * x)) ** 2 for x, y in points)


best = None
for b0, b1 in lines:
    r = rss(b0, b1)
    print(f"b0={b0}, b1={b1}: RSS = {r:.2f}")
    if best is None or r < best[0]:
        best = (r, b0, b1)
print(f"best line: b0={best[1]}, b1={best[2]}")
```

Hand-trace the program and write **every line it prints**, in order, in `answer.txt`. Do not run the code before you have written your answer.

## Example

For `points = [(1, 1)]` and a line `(0.0, 3.0)` the gap is `1 - 3 = -2`, squared `4`, and the program would print `b0=0.0, b1=3.0: RSS = 4.00`.

## After you answer

- Which of the three lines is the least-squares line? Check it with the formula from the previous problem.
