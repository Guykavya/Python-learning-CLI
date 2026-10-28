# comb, perm, gcd, lcm and isqrt

The `math` module has exact **integer** functions for counting and number theory. They work for
integers of any size, because they never go through a `float`.

Write in `solution.py`:

1. `handshakes(n) -> int`: each of `n` people shakes hands once with every other person. How
   many handshakes? (Order does not matter: use `math.comb`.)
2. `podium_orders(n, k=3) -> int`: how many different ordered podiums (1st, 2nd, 3rd, ...) of `k`
   places can `n` runners make? (Order matters: use `math.perm`.)
3. `simplify(num, den) -> tuple[int, int]`: the fraction in lowest terms, with the sign on the
   numerator and a positive denominator. `den == 0` raises `ZeroDivisionError`.
4. `first_common_time(intervals) -> int`: buses all leave at minute 0, bus `i` then every
   `intervals[i]` minutes. At which minute do they all leave together again? An empty list or an
   interval `<= 0` raises `ValueError`.
5. `is_perfect_square(n) -> bool`: `True` if `n == k * k` for some integer `k`. Must be exact for
   huge numbers. Negative numbers give `False`.

**Examples**

```python
handshakes(4)                 # 6
podium_orders(8)              # 336
simplify(3, -9)               # (-1, 3)
first_common_time([4, 6])     # 12
is_perfect_square((10**20 + 1) ** 2)   # True
```
