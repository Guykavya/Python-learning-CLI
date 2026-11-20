# Climbing stairs with a set of steps

Now the allowed move lengths are given as a list. Write `count_ways(n, steps)` that returns the number of different **sequences of moves** that climb from step 0 to exactly step `n`, where every move is one of the numbers in `steps`. Return the count **modulo `10**9 + 7`**.

Order matters: with steps `[1, 3]`, the sequences `1 + 3` and `3 + 1` are two different ways.

## Example

```python
>>> count_ways(4, [1, 2])           # the ordinary staircase
5
>>> count_ways(5, [1, 3, 4])        # 11111, 113, 131, 311, 14, 41
6
>>> count_ways(7, [2])              # an odd number of steps cannot be made of 2s
0
>>> count_ways(0, [5, 9])           # already there: the empty sequence
1
>>> count_ways(3, [5, 9])           # every move is too long
0
```

## Constraints

- `0 <= n <= 10**4`; `steps` has 1 to 60 **different** positive integers, in any order. Some may be bigger than `n`.
- Expected `O(n * len(steps))`. A recursion `n` deep is too deep for Python at `n = 10**4`: fill a table.

## Think about

Chapter section 7 ends with a remark: climbing with a set of steps is the same DP as one of the two coin-counting loops. Which one, combinations or sequences? Why?
