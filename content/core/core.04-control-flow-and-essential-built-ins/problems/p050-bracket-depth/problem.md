# Bracket depth checker

The first line is a number `N`. Then come `N` lines of text. For each line, check its round
brackets `(` and `)`. Other characters are ignored.

- If a `)` appears when no `(` is open, print
  `Unbalanced: unexpected ')' at position P` (P counts from 0) and stop checking that line.
- Otherwise, if some `(` are still open at the end, print `Unbalanced: K unclosed '('`.
- Otherwise print `Balanced, max depth D`, where `D` is the largest number of brackets open
  at the same time (0 if there are none).

Finally print `Balanced: B of N`.

**Example**

Input:
```
3
(a + (b * c))
)(
((x)
```
Output:
```
Balanced, max depth 2
Unbalanced: unexpected ')' at position 0
Unbalanced: 1 unclosed '('
Balanced: 1 of 3
```
