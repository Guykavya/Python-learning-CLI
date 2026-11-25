# Which assumption is broken?

Chapter section 9. Four numbers summarise a fitted line: the funnel ratio, the Durbin-Watson statistic, the largest Cook's distance and the Jarque-Bera p-value. A small rule turns them into a label. The rules are checked **in order**: the first one that applies wins.

```python
def label(funnel, dw, max_cooks, jb_p):
    if funnel > 2:
        return "non-constant variance"
    if dw < 1.5 or dw > 2.5:
        return "correlated errors"
    if max_cooks > 1:
        return "influential point"
    if jb_p < 0.05:
        return "non-normal errors"
    return "no problem found"


cases = [
    ("A", 2.9, 2.0, 0.05, 0.40),
    ("B", 1.1, 0.9, 0.03, 0.50),
    ("C", 1.2, 2.1, 1.40, 0.30),
    ("D", 1.0, 2.0, 0.04, 0.01),
    ("E", 1.3, 2.6, 0.02, 0.60),
    ("F", 2.2, 0.8, 1.20, 0.001),
    ("G", 1.0, 1.9, 0.30, 0.45),
]
for name, funnel, dw, cooks, jb_p in cases:
    print(f"{name}: {label(funnel, dw, cooks, jb_p)}")
```

Hand-trace the program and write **every line it prints**, in order, in `answer.txt`. Do not run the code before you have written your answer.

## Example

For a case `("Z", 1.0, 2.0, 0.1, 0.5)` the program would print `Z: no problem found`.

## After you answer

- Case F breaks three rules at once. Why is only one label printed, and is that a good diagnostic report?
