# Fix the longest subarray with sum k

`starter.py` reads `n`, `k` and an array of integers (negatives allowed), and prints the **length of the longest
contiguous subarray whose sum is exactly `k`** (or `0` if there is none). It uses prefix sums and a dictionary and it is almost
right. It has **three bugs**. Find them and fix them. Do not rewrite from scratch: each fix is one or two lines.

Where to look, without saying what is wrong:

1. If the prefix sum so far is `total` and you want a block that adds up to `k`, which earlier prefix sum do you need?
2. What is the prefix sum **before** the first element, and where is it in the dictionary?
3. If the same prefix sum appears at two indices, which index gives the **longest** block?

## Input

- Line 1: `n k`.
- Line 2: `n` integers.

## Output

One integer.

## Example

Input:

```
5 3
1 -1 5 -2 3
```

Output:

```
4
```

The block `1 -1 5 -2` has sum 3 and length 4. The block `3` has sum 3 but length 1.

## Constraints

- `1 <= n <= 200000`
- `-10^9 <= a[i], k <= 10^9`
