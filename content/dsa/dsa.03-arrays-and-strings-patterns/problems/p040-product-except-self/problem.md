# Product of everything except self

For every position `i`, print the product of all elements **except** `a[i]`. Do it **without division**: the array
may contain zeros, and with a zero you cannot divide the total product by `a[i]`.

The products get huge, so print each one **modulo `10^9 + 7`**, as a number from `0` to `10^9 + 6`. (In Python,
`x % MOD` is never negative, even when `x` is.) The product of no numbers at all is `1`.

## Input

- Line 1: `n`.
- Line 2: `n` integers.

## Output

One line: `n` values separated by single spaces, the `i`-th being the product of all elements except `a[i]`,
modulo `10^9 + 7`.

## Example

Input:

```
4
1 2 3 4
```

Output:

```
24 12 8 6
```

For position 2 (value 2): `1 * 3 * 4 = 12`.

## More examples

- `2 0 3` gives `0 6 0`: only the position of the zero has a non-zero product (`2 * 3`).
- `-1 2` gives `2 1000000006`: the second answer is `-1`, and `-1 % (10^9 + 7) = 10^9 + 6`.
- `5` (one element) gives `1`: the product of nothing.

## Constraints

- `1 <= n <= 200000`
- `-10^9 <= a[i] <= 10^9`

Use `input()` without a prompt message.
