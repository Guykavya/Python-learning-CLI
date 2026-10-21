## Approach

A loop-and-a-half reads commands. `match` on the word list checks the shape and captures the
number in one step.

## Code

```python
counter = 0
while True:
    line = input().strip()
    match line.split():
        case []:
            continue
        case ["quit"]:
            break
        case ["add", n]:
            counter += int(n)
        case ["sub", n]:
            counter -= int(n)
        case ["add" | "sub"]:
            print("Missing number")
        case ["double"]:
            counter *= 2
        case ["reset"]:
            counter = 0
        case ["show"]:
            print(f"Counter: {counter}")
        case _:
            print(f"Unknown command: {line}")
print(f"Final: {counter}")
```

## Why `break` inside `match` leaves the loop

`match` is not a loop. `break` and `continue` inside it act on the nearest enclosing loop,
the `while`.

## Why `add 1 2` is unknown

`["add", n]` matches exactly two words. Three words do not fit any pattern except the
wildcard. Sequence patterns check the length as well as the contents.
