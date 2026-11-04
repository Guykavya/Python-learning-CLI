# Shortest subarray with sum at least s

All numbers in the array are **positive**. Find the length of the shortest subarray (a run of neighbouring
elements) whose sum is **at least** `s`. Print `0` if no subarray reaches `s`, not even the whole array.

## Input

- Line 1: `n` and `s`.
- Line 2: `n` positive integers.

## Output

One line: the smallest length, or `0`.

## Example

Input:

```
6 7
2 3 1 2 4 3
```

Output:

```
2
```

`4 3` sums to 7 with length 2. No single element reaches 7.

## Constraints

- `1 <= n <= 200000`
- `1 <= a[i] <= 10^4`
- `1 <= s <= 10^9`

Because every number is positive, adding an element always makes a sum bigger and removing one always makes it
smaller. That is what makes a sliding window work. Use `input()` without a prompt message.
