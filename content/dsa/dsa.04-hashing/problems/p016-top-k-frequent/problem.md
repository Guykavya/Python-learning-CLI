# Top k frequent values

Given `n` integers and a number `k`, print the `k` values that occur most often. Order the output by **count,
largest first**, and break ties by **smaller value first**. It is guaranteed that `k` is at most the number of
distinct values.

## Input

- Line 1: `n k`.
- Line 2: `n` integers.

## Output

One line: the `k` values separated by spaces.

## Example

Input:

```
8 2
1 1 1 2 2 3 3 4
```

Output:

```
1 2
```

Counts: `1` three times, `2` twice, `3` twice, `4` once. The top two by count are `1` and then a tie between `2`
and `3`; the smaller value `2` wins.

## Constraints

- `1 <= k <= number of distinct values <= n <= 200000`
- `-10^9 <= a[i] <= 10^9`
