# Ask for a number, with limited attempts

Write `ask_float(prompt, low, high, ask=input, tell=print, attempts=3)` that asks the user for a
number from `low` to `high` (inclusive) and returns it as a float.

`ask` and `tell` are passed in so that tests can replace the keyboard and the screen (section 16).
Call `ask(prompt)` to read an answer and `tell(message)` to show a message. Never call `input` or
`print` directly.

1. If `attempts` is less than 1, raise `ValueError("attempts must be at least 1")` **before**
   asking anything.
2. On each attempt, read `text = ask(prompt)` and convert with `float(text)`.
   - Not a number: `tell(f"{text!r} is not a number. Type something like {low}.")`
   - A number outside the range: `tell(f"Please choose from {low} to {high}, got {value}.")`.
     (`nan` fails every comparison, so it is "outside the range" automatically.)
   - Otherwise return the value.
3. After `attempts` failed answers, raise
   `ValueError(f"no valid answer after {attempts} attempts")`.

If `ask` raises `EOFError` (input ran out), do **not** catch it: there is nothing to retry.

**Example**

```python
answers = iter(["lots", "12", "4.5"])
messages = []
ask_float("Hours slept? ", 0, 10, ask=lambda p: next(answers), tell=messages.append)
# 4.5
messages
# ["'lots' is not a number. Type something like 0.", 'Please choose from 0 to 10, got 12.0.']
```
