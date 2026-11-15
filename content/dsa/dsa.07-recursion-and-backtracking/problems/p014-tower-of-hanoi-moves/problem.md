# Tower of Hanoi moves

There are three pegs. On peg `source` there are `n` discs, the largest at the bottom and the smallest on top. Move the whole tower to peg `target`. Rules:

- move one disc at a time (the top disc of a peg);
- never put a larger disc on a smaller one.

Write `hanoi(n, source="A", target="C", spare="B")` that returns the list of moves of the shortest solution, each move a tuple `(from_peg, to_peg)`.

## Example

```python
>>> hanoi(1)
[('A', 'C')]
>>> hanoi(2)
[('A', 'B'), ('A', 'C'), ('B', 'C')]
>>> len(hanoi(10))
1023
>>> hanoi(1, "X", "Y", "Z")
[('X', 'Y')]
```

## Constraints

- `0 <= n <= 15`; `hanoi(0)` is `[]`.

## Think about

To move the **largest** disc from `source` to `target`, the other `n - 1` discs must all be on `spare` first. That is a smaller Hanoi problem. What comes after the big move?
