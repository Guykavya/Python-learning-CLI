# The step-size trap

Chapter section 6.3. A one-sided difference has a **truncation error** that grows with `h` and a **rounding error** that grows when `h` is tiny. The program labels how large the error of the forward difference of `x^2` at `x = 1` is (the exact derivative is 2).

```python
def f(x):
    return x * x


def label(err):
    if err < 1e-7:
        return "small"
    if err < 1e-2:
        return "medium"
    return "large"


for h in [1e-1, 1e-5, 1e-8, 1e-15]:
    d = (f(1 + h) - f(1)) / h
    print(f"h={h:.0e}: {label(abs(d - 2))}")
```

Hand-trace the program and write **every line it prints**, in order, in `answer.txt`. Do not run the code before you have written your answer.

## Example

For `h = 1e-3` the forward difference is `2.001`, the error is `1e-3`, so the line would read `h=1e-03: medium`.

## After you answer

- Why is the best `h` neither the biggest nor the smallest one?
- Which `h` would you choose, and for which formula?
