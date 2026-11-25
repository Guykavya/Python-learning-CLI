## Hint 1

Count the work: to get `inv(A)`, how many systems does NumPy have to solve (one per column of the identity)? How many does `solve(A, b)` solve? Then compare the two Hilbert errors in fact 1.

## Hint 2

In fact 2, the two equations are `x + y = 2` and `x + 1.0001 y = 2.0001`. Draw them: two almost parallel lines. What happens to their crossing point when one line moves a tiny bit? That sensitivity is what the condition number measures.

## Hint 3

```text
work:      inv = factorise + n solves + multiply;  solve = factorise + 1 solve
accuracy:  more steps, more rounding; Hilbert 1.69e-04 vs 5.55e-03
cond:      amplification of input errors; 4e4 here, 1.6e13 for Hilbert -> ~16 - 13 = 3 good digits
residual:  A @ x - b small = equations satisfied; with large cond, x can still be far off
inverse:   only when you need the matrix itself (e.g. regression standard errors)
```
