# Explain: read this mypy error

Ravi saves this program as `orders.py`:

```python
def total_price(prices: list[float], tax: float) -> float:
    return sum(prices) * (1 + tax)


print(total_price([10.0, 20.0], "0.18"))
```

He runs `python -m mypy orders.py` and sees:

```text
orders.py:5: error: Argument 2 to "total_price" has incompatible type "str"; expected "float"  [arg-type]
Found 1 error in 1 file (checked 1 source file)
```

In `answer.md` (about 120 to 250 words), explain:

1. What does each part of the error line mean: `orders.py:5`, `Argument 2`, `"str"`, `"float"`, and `[arg-type]`?
2. Where is the mistake: in the function `total_price` or in the call? Which of the two would you change, and how?
3. If Ravi runs `python orders.py` instead, what happens? Does the hint stop him? (Think about what `1 + "0.18"` does.)
4. Why is it still useful that mypy found this before the program ran?
