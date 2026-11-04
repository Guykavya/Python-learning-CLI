# Dutch national flag

The array holds only the values `0`, `1` and `2` (think of the three colours of a flag). Rearrange it so that all
`0`s come first, then all `1`s, then all `2`s, and print it.

Do it **in place, in one pass**, with three pointers, and without `sort()`. The tests only check the printed
result, so counting the three values would also pass; the point of this exercise is the three-pointer
partition, which is the heart of quicksort's three-way split and works when you must move whole records, not
just count numbers.

## Input

- Line 1: `n`.
- Line 2: `n` values, each `0`, `1` or `2`.

## Output

One line: the rearranged array, values separated by single spaces.

## Example

Input:

```
6
2 0 2 1 1 0
```

Output:

```
0 0 1 1 2 2
```

## Constraints

- `1 <= n <= 200000`

Use `input()` without a prompt message.
