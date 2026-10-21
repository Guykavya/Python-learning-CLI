# Towers of Hanoi

Three pegs, `A`, `B` and `C`. On peg `source` sit `n` discs, largest at the bottom. Move them all
to peg `target`, one disc at a time, never putting a larger disc on a smaller one, using `spare`
as a helper.

Write `hanoi(n, source="A", target="C", spare="B")` that returns the list of moves, each a tuple
`(from_peg, to_peg)`, using the minimum number of moves (`2**n - 1`).

**Examples**

```python
hanoi(0)    # []
hanoi(1)    # [('A', 'C')]
hanoi(2)    # [('A', 'B'), ('A', 'C'), ('B', 'C')]
hanoi(2, source="X", target="Y", spare="Z")   # [('X', 'Z'), ('X', 'Y'), ('Z', 'Y')]
len(hanoi(10))   # 1023
```
