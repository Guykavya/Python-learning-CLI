## Hint 1

The answer is either a number or a name. `int(answer)` tells you which: what does it raise for
`"coffee"`?

## Hint 2

Use `try` / `except ValueError` (the answer is not a number, so look for a name) / `else` (it is
a number, so check the range). If neither path returned, the answer was bad: tell and loop.

## Hint 3

```
while True:
    text = ask(prompt); answer = text.strip()
    try: number = int(answer)
    except ValueError:
        for option in options: if names match ignoring case: return option
    else:
        if 1 <= number <= len(options): return options[number - 1]
    tell(...)
```
