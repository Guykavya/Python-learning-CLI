# Values in both lists

Two lists of integers are given. Print how many **distinct** values appear in **both**, and then those values in
increasing order.

Sets make this easy: `set(a) & set(b)` is the intersection. Looping over both lists to compare each pair would be
`n * m` steps.

## Input

- Line 1: `n m`.
- Line 2: the `n` integers of list A.
- Line 3: the `m` integers of list B.

## Output

- Line 1: the number `c` of distinct common values.
- Line 2: the common values in increasing order, separated by spaces (an empty line when `c = 0`).

## Example

Input:

```
5 4
1 2 2 3 7
2 2 7 9
```

Output:

```
2
2 7
```

`2` appears in both lists (twice in each), but is counted once. `1`, `3`, `9` appear in only one list.

## Constraints

- `1 <= n, m <= 200000`
- `-10^9 <= value <= 10^9`
