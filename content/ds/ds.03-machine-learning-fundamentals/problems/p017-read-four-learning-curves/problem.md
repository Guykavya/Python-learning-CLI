# Read four learning curves

Chapter section 7. Four models were trained on growing amounts of data. Only the **last row** of each learning curve matters for the diagnosis. The rule is the one from the previous problem, with a noise floor of 0.30.

```python
def diagnose(train, val, floor=0.30):
    gap = val - train
    if gap / val > 0.15:
        return "high variance"
    if val > 1.25 * floor:
        return "high bias"
    return "fine"


curves = {
    "A": [(10, 0.00, 3.10), (80, 0.04, 0.95), (320, 0.05, 0.90)],
    "B": [(10, 0.42, 0.70), (80, 0.49, 0.56), (320, 0.50, 0.53)],
    "C": [(10, 0.20, 0.45), (80, 0.27, 0.34), (320, 0.29, 0.31)],
    "D": [(10, 0.10, 0.60), (80, 0.17, 0.30), (320, 0.20, 0.27)],
}
for name, rows in curves.items():
    n, train, val = rows[-1]
    print(f"curve {name} (n = {n}): {diagnose(train, val)}")
```

Hand-trace the program and write **every line it prints**, in order, in `answer.txt`. Do not run the code before you have written your answer.

## Example

For a curve whose last row is `(100, 0.30, 0.32)` the line would be `curve X (n = 100): fine`.

## After you answer

- Curve D has a lower validation error than C and is called high variance. Is the rule too strict, or is D really worse? What would you check next?
