## Approach

`int()` acts as the test "is this a number?" (EAFP). If it fails, the handler searches the
options by name. If it succeeds, `else` checks the range; this check matters because Python
would happily accept `options[-1]`. Any path that does not `return` falls through to the
message, and the `while True` loop asks again. `ask` is outside the `try`, so `EOFError`
propagates.

## Code

```python
def choose(options, ask=input, tell=print):
    """Ask until the user picks an option by number (from 1) or by name; return it."""
    if not options:
        raise ValueError("options must not be empty")
    prompt = f"Choose 1-{len(options)} or a name: "
    while True:
        text = ask(prompt)
        answer = text.strip()
        try:
            number = int(answer)
        except ValueError:
            for option in options:
                if option.lower() == answer.lower():
                    return option
        else:
            if 1 <= number <= len(options):
                return options[number - 1]
        tell(f"{text!r} is not an option. Type a number from 1 to {len(options)} or a name.")
```

## Complexity

O(n) per answer for n options (the name search).

## Another way

Build a dict from lower-cased name to option once, before the loop, so the name lookup is O(1):
`by_name = {o.lower(): o for o in options}`. Then the handler is `by_name.get(answer.lower())`.
