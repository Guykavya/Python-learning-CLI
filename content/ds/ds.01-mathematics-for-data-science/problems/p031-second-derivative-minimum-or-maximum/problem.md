# Second derivative: minimum or maximum?

Chapter section 6.6. At a point where the slope is 0, the **second derivative** tells the shape: positive means a valley (minimum), negative a hill (maximum), and zero means *this test cannot decide*. The program estimates the second derivative numerically and labels the point.

```python
def classify(f, x0, h=1e-3):
    d2 = (f(x0 + h) - 2 * f(x0) + f(x0 - h)) / h ** 2
    if d2 > 1e-4:
        return "minimum"
    if d2 < -1e-4:
        return "maximum"
    return "flat"


cases = [
    ("x^2", lambda x: x ** 2),
    ("-x^2", lambda x: -x ** 2),
    ("x^3", lambda x: x ** 3),
    ("x^4", lambda x: x ** 4),
]
for name, f in cases:
    print(f"{name} at 0: {classify(f, 0.0)}")
```

Hand-trace the program and write **every line it prints**, in order, in `answer.txt`. Do not run the code before you have written your answer.

## Example

For `f(x) = 5 x^2` the estimate is `10`, so the line would be `5x^2 at 0: minimum`.

## After you answer

- One of the labels says "flat" for a function that really has a minimum. Which one, and what does it teach about the test?
