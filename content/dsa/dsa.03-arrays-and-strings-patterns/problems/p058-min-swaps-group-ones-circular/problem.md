# Minimum swaps to group all ones in a circle

An array of `0`s and `1`s is arranged in a **circle**: the last element is next to the first. A **swap** exchanges
the values of any two positions (they do not have to be neighbours). What is the smallest number of swaps that
puts all the `1`s next to each other, in one block around the circle?

Let `m` be the number of `1`s. At the end, the `1`s fill some block of `m` consecutive positions (possibly wrapping
around the end). If that block already holds `w` ones, it holds `m - w` zeros, and each zero needs exactly one swap
with a `1` from outside. So:

```
answer = m - (largest number of 1s in any circular window of size m)
```

A circular window can be handled without copying the array: walk `i` from 0 to `n + m - 1` and read `a[i % n]`.

## Input

- Line 1: `n`.
- Line 2: `n` values, each `0` or `1`.

## Output

One line: the minimum number of swaps.

## Example

Input:

```
7
0 1 0 1 1 0 0
```

Output:

```
1
```

There are 3 ones, so the final block has size 3. The window at positions 3 to 5 is `0 1 1`: it already holds 2 ones
and needs one more. Swap its 0 (position 3) with the lone 1 at position 2: the array becomes `0 0 1 1 1 0 0`. No window
of size 3 holds 3 ones, so 0 swaps is impossible, and the answer is `3 - 2 = 1`.

Circular example: `1 1 0 0 1` needs **0** swaps: the last 1 is next to the first two around the circle.

## Constraints

- `1 <= n <= 200000`
- If there are no `1`s at all, the answer is 0.

Use `input()` without a prompt message.
