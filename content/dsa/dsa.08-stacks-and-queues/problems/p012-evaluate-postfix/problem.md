# Evaluate a postfix expression

Write `eval_rpn(tokens)` that evaluates an expression in **postfix** (reverse Polish) notation. `tokens` is a list of strings; each is an integer (possibly negative, like `"-11"`) or one of `+ - * /`.

- a number: push it;
- an operator: pop the **right** operand `b` first, then the left operand `a`, compute `a op b`, push the result.

At the end exactly one number is left: return it (chapter section 6, "Postfix").

**Division truncates toward zero**, as in C or Java: `7 / 2` is `3`, `-7 / 2` is `-3`, `7 / -2` is `-3`. Python's `//` rounds toward minus infinity (`-7 // 2` is `-4`), so you need your own helper. Do **not** use `int(a / b)`: it goes through floats and is wrong for very large numbers (one test has a 19-digit number).

## Example

```python
>>> eval_rpn(["2", "1", "+", "3", "*"])
9
>>> eval_rpn(["4", "13", "5", "/", "+"])
6
>>> eval_rpn(["10", "6", "9", "3", "+", "-11", "*", "/", "*", "17", "+", "5", "+"])
22
>>> eval_rpn(["-7", "2", "/"])
-3
```

## Constraints

- The expression is always valid; no division by zero.
- `1 <= len(tokens) <= 10**4`.

## Think about

How do you tell the number `"-11"` from the operator `"-"`? (Checking `t[0].isdigit()` is not enough.)
