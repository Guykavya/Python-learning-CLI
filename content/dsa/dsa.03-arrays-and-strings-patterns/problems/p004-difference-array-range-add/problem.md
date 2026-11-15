# Range additions with a difference array

You get an array and `q` updates. Each update `l r v` adds `v` to every element from position `l` to position `r`
(1-based, inclusive). After all updates, print the array.

Adding `v` to each element of each range costs up to `n * q` steps: 4 * 10^10 for the biggest input. Instead keep a
**difference array** `d` of size `n + 2`, all zeros:

- for an update `l r v`: `d[l] += v` and `d[r + 1] -= v` (two steps, whatever the range length);
- at the end, walk `i = 1 .. n` with a running total of `d`; that total is how much was added to position `i`.

The `+v` at `l` "switches the addition on" for everything to its right, and the `-v` at `r + 1` switches it off again.

## Input

- Line 1: `n`.
- Line 2: `n` integers, the starting array.
- Line 3: `q`.
- Next `q` lines: `l r v`.

## Output

One line: the final array, separated by spaces.

## Example

Input:

```
5
1 1 1 1 1
3
1 3 2
2 5 10
5 5 -4
```

Output:

```
3 13 13 11 7
```

After `1 3 2`: `3 3 3 1 1`. After `2 5 10`: `3 13 13 11 11`. After `5 5 -4`: `3 13 13 11 7`.

## Constraints

- `1 <= n <= 200000`, `0 <= q <= 200000`
- `1 <= l <= r <= n`, `-10^9 <= v, a[i] <= 10^9`
