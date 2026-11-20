# Jump game as DP

`nums[i]` is the **maximum** jump length from index `i`: from `i` you may land on any index `i + 1 .. i + nums[i]`. You start at index 0. Write `min_jumps(nums)` that returns the **fewest jumps** needed to reach the last index, or `-1` if the last index cannot be reached.

In dsa.13 (jump game II) the last index was always reachable and a greedy layer scan solved it. Here you solve it with the DP recipe of chapter section 2, the way section 5 solves one-dimensional problems, and you must also detect "impossible".

## Example

```python
>>> min_jumps([2, 3, 1, 1, 4])      # 0 -> 1 -> 4
2
>>> min_jumps([3, 2, 1, 0, 4])      # every route stops on index 3
-1
>>> min_jumps([0])                  # already on the last index
0
>>> min_jumps([1, 0, 5])
-1
```

## Constraints

- `1 <= len(nums) <= 400`, `0 <= nums[i] <= 50`.
- A plain recursion that tries every jump from every index is exponential: `[3] * 400` must finish quickly. Use a table (or a memo).

## Think about

1. State: what does `f[i]` mean? Use the sentence "the fewest jumps to **arrive** at index `i`".
2. Which value of `f` means "cannot get here"? Section 7 used `INF` for the same job in coin change. Why does `INF + 1` help?
3. If you fill `f` from left to right, every index that can jump to `j` has already been finished when you reach `j`. Why?
