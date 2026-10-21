## Approach

A `for` loop gives at most three attempts. `break` stops it as soon as the PIN is right,
which also stops reading input.

## Code

```python
pin = input().strip()
for left in range(2, -1, -1):
    if input().strip() == pin:
        print("Welcome")
        break
    if left > 0:
        word = "try" if left == 1 else "tries"
        print(f"Wrong PIN. {left} {word} left")
    else:
        print("Wrong PIN. Card blocked")
```

## Why count down

`range(2, -1, -1)` gives 2, 1, 0: exactly "tries left after this one". The stop is -1
because the stop value is never included.

## Another way: loop else

```python
for attempt in range(1, 4):
    if input().strip() == pin:
        print("Welcome")
        break
    if attempt < 3:
        print(f"Wrong PIN. {3 - attempt} ...")
else:
    print("Wrong PIN. Card blocked")
```

Here the `else` runs only when no `break` happened, which is exactly "all three failed".
The third wrong attempt prints nothing inside the loop.
