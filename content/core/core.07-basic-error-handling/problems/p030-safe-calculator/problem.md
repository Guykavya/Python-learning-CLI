# A calculator that never crashes

Write `calculate(expression)` for a one-line calculator. The user types two numbers and an
operator separated by spaces, for example `"12 / 4"`. Return the result as a string, or an error
message starting with `"Error: "`. For **any** string, the function must return; it must never
raise.

1. If `expression` is not a `str`, that is a programming bug: raise
   `TypeError(f"expression must be text (str), got {type(expression).__name__}")`.
2. Split on whitespace. Not exactly three parts:
   `"Error: write it as <number> <operator> <number>, for example 12 / 4"`
3. Convert the first, then the second number with `float()`. The first that fails, **or** that is
   not finite (`nan`, `inf`):  `f"Error: {text!r} is not a number"`.
4. The operator must be one of `+ - * / // % **`. Otherwise:
   `f"Error: unknown operator {op!r}; use one of + - * / // % **"`.
5. Compute. Division, floor division or remainder by zero:
   `"Error: cannot divide by zero"`.
6. A result that is too large: `"Error: the result is too large"`. Careful: `10.0 ** 400` raises
   `OverflowError`, but `1e308 * 10` raises **nothing** and quietly gives `inf`. Handle both.
7. A negative number to a fractional power, such as `-8 ** 0.5`, gives a **complex** number in
   Python: `"Error: the result is not a real number"`.
8. Otherwise return `str(result)`, for example `"3.0"`.

**Examples**

```python
calculate("12 / 4")        # '3.0'
calculate("2 ** 10")       # '1024.0'
calculate("7 // 2")        # '3.0'
calculate("12 /")          # 'Error: write it as <number> <operator> <number>, for example 12 / 4'
calculate("12 x 4")        # "Error: unknown operator 'x'; use one of + - * / // % **"
calculate("ten / 2")       # "Error: 'ten' is not a number"
calculate("5 % 0")         # 'Error: cannot divide by zero'
calculate("1e308 * 10")    # 'Error: the result is too large'
calculate("-8 ** 0.5")     # 'Error: the result is not a real number'
```

A dispatch table (chapter 6), a dict from operator text to a function, keeps step 5 short.
