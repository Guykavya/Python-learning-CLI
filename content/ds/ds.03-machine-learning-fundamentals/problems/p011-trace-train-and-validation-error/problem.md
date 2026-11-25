# Trace train and validation error

Chapter section 5. Here are the errors of six polynomial models of a noisy sine (the noise floor, the best any model can do, is about 0.30). A small rule labels each degree.

```python
errors = {
    1: (0.50, 0.52),
    2: (0.48, 0.50),
    3: (0.29, 0.31),
    6: (0.25, 0.33),
    9: (0.12, 0.90),
    12: (0.05, 4.10),
}
FLOOR = 0.30


def verdict(train, val):
    if train > 1.3 * FLOOR:
        return "underfit"
    if val > 1.5 * train:
        return "overfit"
    return "good"


for degree, (train, val) in errors.items():
    print(f"degree {degree:2d}: {verdict(train, val)}")
best = min(errors, key=lambda d: errors[d][1])
print(f"lowest validation error: degree {best}")
```

Hand-trace the program and write **every line it prints**, in order, in `answer.txt`. Do not run the code before you have written your answer.

## Example

For the entry `4: (0.28, 0.30)` the line would be `degree  4: good` (note the width-2 format puts a space before a one-digit degree).

## After you answer

- Degree 6 has a lower **training** error than degree 3 but is labelled `good` too. Why is degree 3 still the better choice?
