## Approach

Validate the shape, then the counts. Compute "has X won?" and "has O won?" with `any` over the
eight lines, each line checked with `all`. Finally, apply the turn rules.

## Code

```python
r1 = input()
r2 = input()
r3 = input()
b = r1 + r2 + r3
x = b.count("X")
o = b.count("O")

shape_ok = len(r1) == len(r2) == len(r3) == 3 and all(ch in "XO." for ch in b)
if not shape_ok or not (x == o or x == o + 1):
    print("Invalid board")
else:
    wins = ""
    for p in "XO":
        won = False
        for i in range(3):
            row = all(b[3 * i + c] == p for c in range(3))
            col = all(b[3 * r + i] == p for r in range(3))
            won = won or row or col
        diag1 = all(b[4 * k] == p for k in range(3))        # positions 0, 4, 8
        diag2 = all(b[2 + 2 * k] == p for k in range(3))    # positions 2, 4, 6
        if won or diag1 or diag2:
            wins += p
    if wins == "XO" or (wins == "X" and x != o + 1) or (wins == "O" and x != o):
        print("Invalid board")
    elif wins:
        print(f"{wins} wins")
    elif "." not in b:
        print("Draw")
    else:
        print("In progress")
```

## Why validate counts before winners

A board with five X's and no O's may contain a "winning" row, but it can never happen in a
real game. Every rule in the problem removes a kind of impossible board; check them before
reporting a win.

## Why `str.count` here

`b.count("X")` is a string method from the previous chapter and is the clearest way to count
one character. A loop with a counter would work too.
