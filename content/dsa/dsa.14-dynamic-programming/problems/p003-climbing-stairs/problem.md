# Climbing stairs

You climb a staircase of `n` steps. Each move is **1 or 2** steps. Write `climb_stairs(n)` that returns the number of different ways to reach step `n` from the ground (step 0), **modulo `10**9 + 7`** (`1_000_000_007`).

Two ways are different if their sequences of moves differ: `1 + 2` and `2 + 1` are two ways.

## Example

```python
>>> climb_stairs(3)        # 1+1+1, 1+2, 2+1
3
>>> climb_stairs(4)        # 1+1+1+1, 1+1+2, 1+2+1, 2+1+1, 2+2
5
>>> climb_stairs(0)        # one way to stay on the ground: do nothing
1
>>> climb_stairs(100000)
967618232
```

## Constraints

- `0 <= n <= 10**5`.
- A recursion `n` deep (even with a memo) crashes Python for `n = 10**5` (chapter section 3, trap 2). Use a table or two variables.
- Take the remainder **inside** the loop, not only at the end. The exact count for `n = 10**5` has about 20,000 digits; adding such numbers 100,000 times is slow.

## Think about

Write the state sentence first (chapter section 2): "`f(i)` = the number of ways to ...". The last move into step `i` came from where?
