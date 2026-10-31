## Walkthrough

- **A** Ten roundings, and their small errors add up instead of cancelling: the loop ends at
  `0.9999999999999999`, the float just below 1.
- **B** `fsum` keeps the lost digits and rounds once: `1.0`.
- **C** So the loop result is not equal to `1.0`: `False`. Never use `==` on computed floats.
- **D** The difference is about `1.1e-16`, far below `1e-09 * 1.0`: `True`.
- **E** The famous one: `0.30000000000000004`.
- **F** `fsum([0.1, 0.2])` is the correctly rounded value of the exact sum of the two *stored*
  numbers, which is the same as `0.1 + 0.2` (one `+` is already correctly rounded). It is still
  not the float `0.3`, because the error is in how `0.1` and `0.2` are stored, not in the
  adding. `fsum` cannot fix representation error: `False`.
- **G** Only a relative tolerance: the allowed difference is `1e-09 * 1e-12 = 1e-21`, and the real
  difference is `1e-12`. Nothing non-zero is ever "close" to `0.0` this way: `False`.
- **H** With `abs_tol=1e-9`, a difference of `1e-12` is allowed: `True`.
- **I** `0.0 + 1e16 = 1e16`; `1e16 + 1.0` cannot be stored (floats there are 2 apart) and rounds
  back to `1e16`; then `- 1e16` gives `0.0`. The `1.0` was lost.
- **J** `fsum` keeps the `1.0` aside and gives the exact answer `1.0`.
- **K** Difference 1.0, allowed `0.01 * 101.0 = 1.01`: `True`. `rel_tol=0.01` means "within 1%".
- **L** `2.675` is stored slightly *below* 2.675, so rounding to two places goes down: `2.67`.
  It is not a bug in `round`.
- **M** `floor(-0.5)` is `-1`, `ceil(-0.5)` is `0`, and `round` sends halves to the even
  neighbour: `round(-0.5)` is `0`, `round(1.5)` is `2`, `round(2.5)` is also `2`.

## The exact output

```text
A 0.9999999999999999
B 1.0
C False
D True
E 0.30000000000000004
F False
G False
H True
I 0.0
J 1.0
K True
L 2.67
M -1 0 0 2 2
```
