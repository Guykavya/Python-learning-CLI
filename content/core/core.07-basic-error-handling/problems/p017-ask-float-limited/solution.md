## Approach

A counted loop replaces `while True` because the number of tries is limited. Each round has two
failure modes: an exception from `float` (handled with a narrow `try`) and a range failure (an
`if`). Returning from inside the loop ends it on success; falling out of the loop means every
attempt failed, so the line after the loop raises. `EOFError` comes from `ask`, which is outside
the `try`, so it propagates untouched.

## Code

```python
def ask_float(prompt, low, high, ask=input, tell=print, attempts=3):
    """Ask until a number from low to high is given; give up after `attempts` bad answers."""
    if attempts < 1:
        raise ValueError("attempts must be at least 1")
    for _ in range(attempts):
        text = ask(prompt)
        try:
            value = float(text)
        except ValueError:
            tell(f"{text!r} is not a number. Type something like {low}.")
            continue
        if low <= value <= high:
            return value
        tell(f"Please choose from {low} to {high}, got {value}.")
    raise ValueError(f"no valid answer after {attempts} attempts")
```

## Complexity

O(attempts) calls to `ask`.

## Another way

`for ... else`: put the final `raise` in the loop's `else` block (chapter 4), which runs when the
loop was not ended by `break`. Since success uses `return`, not `break`, a plain line after the
loop is simpler.
