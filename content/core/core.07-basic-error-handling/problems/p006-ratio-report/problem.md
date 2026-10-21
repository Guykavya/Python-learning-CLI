# Ratio with two kinds of failure

A form has two text boxes. Write `ratio(a_text, b_text)` that converts both texts with
`float()` and returns the result of `a / b` as a string with two decimal places.

The two things that can go wrong need **different** messages, so use **two** `except` clauses:

- Either text is not a number: return
  `"Both values must be numbers, like 3 or 2.5."`
- The second value is zero: return `"The second value must not be zero."`

If a value is not text at all (for example `None`), `float` raises `TypeError`. That is a bug in
the caller: let it propagate.

**Examples**

```python
ratio("7", "2")        # '3.50'
ratio("1", "3")        # '0.33'
ratio("seven", "2")    # 'Both values must be numbers, like 3 or 2.5.'
ratio("4", "0")        # 'The second value must not be zero.'
ratio("4", "0.0")      # 'The second value must not be zero.'
```
