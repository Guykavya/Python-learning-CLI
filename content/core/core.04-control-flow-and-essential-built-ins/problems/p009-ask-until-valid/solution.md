## Approach

A loop-and-a-half: read, count, check, and either leave or complain. Short-circuit `and`
protects `int()` from text that is not a number.

## Code

```python
attempts = 0
while True:
    text = input().strip()
    attempts += 1
    if text.isdigit() and 1 <= int(text) <= 10:
        break
    print(f"Invalid: {text}")
word = "attempt" if attempts == 1 else "attempts"
print(f"Accepted {int(text)} after {attempts} {word}")
```

## Why `isdigit()` first

`and` evaluates its right side only when the left side is truthy. For `"ten"`, `isdigit()` is
`False`, so `int("ten")` never runs. Swap the two sides and the program crashes.

## Why print `int(text)`

`"07"` is valid (it is 7). Printing `int(text)` shows `7`, not `07`.

## Another way

A flag variable `valid = False` and `while not valid:`. It works but needs the check written
in a way that also sets the flag; `break` is shorter.
