## Hint 1

Run `int(" 7")`, `int("+3")`, `int("1_0")` and `int("²")` in the REPL. Then run `.isdigit()` on
each. Which one should decide?

## Hint 2

Two separate reasons to reject: `int` fails (an exception), or the value is out of range (an `if`).

## Hint 3

```
for token in tokens:
    try:
        value = int(token)
    except ValueError:
        rejected.append(token); continue
    if 0 <= value <= 100: scores.append(value)
    else: rejected.append(token)
```
