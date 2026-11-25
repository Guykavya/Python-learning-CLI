## Hint 1

`astype(int)` does not round at all: in which direction does it move a number? `np.round` sends an exact half to which neighbour? And `.tolist()` of a float array gives floats: how does Python print a negative zero?

## Hint 2

```text
astype(int): cut towards zero      2.5 -> 2, -1.7 -> -1, 1e10 -> 10000000000
np.round:    halves to the EVEN    0.5 -> 0, 1.5 -> 2, 2.5 -> 2, -0.5 -> -0.0
floor: down, ceil: up, int(): towards zero
2.675 is stored as 2.67499999999999982236431605997495353221893310546875 (a bit below)
np.round(v, 2) computes round_half_even(v * 100) / 100, and 2.675 * 100 is exactly 267.5 in float64
Python's round(v, 2) looks at the exact stored value
```
