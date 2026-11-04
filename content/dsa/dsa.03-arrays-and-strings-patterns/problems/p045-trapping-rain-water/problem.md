# Trapping rain water

Bars of width 1 stand side by side; bar `i` has height `h[i]`. Rain falls and fills every dip. How many units of water
stay on top of the bars? Water over the first and the last bar runs off the sides.

The water above bar `i` reaches the level `min(highest bar to its left, highest bar to its right)` (both including
bar `i` itself), so bar `i` holds

```
water[i] = min(max(h[0..i]), max(h[i..n-1])) - h[i]
```

Including bar `i` in both maxima makes `water[i]` never negative. Summing this with two nested scans is O(n^2). Do it in
O(n): either with a prefix-maximum array and a suffix-maximum array, or with **two pointers** and no extra arrays.

## Input

- Line 1: `n`.
- Line 2: `n` heights. When `n = 0` this line is empty.

## Output

One line: the total trapped water.

## Example

Input:

```
12
0 1 0 2 1 0 1 3 2 1 2 1
```

Output:

```
6
```

```
       #
   #~~~##~#
 #~##~######
```

Bar 2 holds 1, bars 4, 5, 6 hold 1, 2, 1, and bar 9 holds 1: `1 + 1 + 2 + 1 + 1 = 6`.

## Constraints

- `0 <= n <= 200000`
- `0 <= h[i] <= 10^9`

Use `input()` without a prompt message.
