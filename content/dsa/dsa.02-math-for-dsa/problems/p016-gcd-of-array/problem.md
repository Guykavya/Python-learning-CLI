# GCD of a whole array

The gcd of several numbers can be built one number at a time: `gcd(a, b, c) = gcd(gcd(a, b), c)`. Fold
the array from left to right, keeping the gcd so far. (Write the two-number gcd yourself with Euclid's loop.)

Given an array `a`, print three lines:

1. `g`, the gcd of all elements;
2. how many elements are equal to `g`;
3. the sum of `a[i] // g` over all elements (the array after dividing everything by `g`).

## Input

- Line 1: `n`.
- Line 2: `n` integers.

## Output

Three lines as described.

## Example

Input:

```
5
12 18 30 6 42
```

Output:

```
6
1
18
```

The gcd is 6. Only one element equals 6. After dividing by 6 the array is 2 3 5 1 7, with sum 18.

## Constraints

- `1 <= n <= 200000`
- `1 <= a[i] <= 10^18`

Use `input()` without a prompt message.
