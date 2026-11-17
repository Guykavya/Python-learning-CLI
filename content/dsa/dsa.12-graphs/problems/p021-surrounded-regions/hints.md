## Hint 1

Checking every region "does it touch the border?" works, but think the other way round: which `"O"` cells are **safe**? Every safe cell is connected to an `"O"` on the border. Can one search, started from **all** border `"O"` cells at once, find every safe cell?

## Hint 2

```
safe = set of all border cells that are "O"; queue/stack = list(safe)
while stack:
    pop (r, c); for each 4-neighbour inside the board that is "O" and not safe: add it to safe and push it
result = for each row r: "".join("O" if (r, c) in safe else "X" for every column c)
```

A `"O"` that is not safe becomes `"X"`, and an `"X"` stays `"X"`.
