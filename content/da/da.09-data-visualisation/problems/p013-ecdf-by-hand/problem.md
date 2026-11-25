# ECDF by hand

Chapter section 4.3. The **empirical cumulative distribution function** (ECDF) answers: "what share of the values is at or below `x`?".
The chapter draws it from the sorted values `xs` against `1/n, 2/n, ..., n/n`.

```python
import numpy as np

values = [3, 1, 2, 2, 5]
xs = np.sort(values)
ys = np.arange(1, len(xs) + 1) / len(xs)
for x, y in zip(xs, ys):
    print(f"{int(x)} {y:.1f}")
print(f"share at or below 2: {(xs <= 2).mean():.1f}")
print(f"jump at 2: {(xs <= 2).mean() - (xs < 2).mean():.1f}")
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`. Do not run the code before you have written your answer.

## Example

For `values = [4, 4]` the loop would print `4 0.5` and `4 1.0`.

## After you answer

- The value 2 appears twice. What does that do to the step of the ECDF at 2?
- Which share does the curve show at x = 2.5?
