## Hint 1

Scan all cells. When you find land that is not yet visited, that is a new island: add 1, then mark every cell of that island as visited so that it is not counted again.

## Hint 2

Recursive fill: `fill(r, c)` returns at once if `(r, c)` is outside, water or visited; otherwise it marks `(r, c)` and calls itself on the four neighbours.

## Hint 3

The same fill with an explicit stack:
```
stack = [(r, c)]; visited.add((r, c))
while stack:
    r, c = stack.pop()
    for each neighbour (nr, nc) that is land and not visited:
        visited.add((nr, nc)); stack.append((nr, nc))
```
