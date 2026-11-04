# Longest free gap in a schedule

A room is open from time `0` to time `T`. Meetings occupy half-open intervals `[l, r)` and may **overlap** and come in **any order**. Find the length of the **longest
stretch of time with no meeting at all**, between `0` and `T` (including the stretch before the first meeting and after the last one).

## Input

- Line 1: `T n`.
- Next `n` lines: `l r` with `0 <= l < r <= T`.

## Output

One integer: the longest free length (`0` if the room is always busy).

## Constraints

- `1 <= T <= 10^9`
- `0 <= n <= 200000`

Sort by start and keep the **furthest end seen so far**; a gap exists when the next start is beyond it. Do not forget the gap before the first start and the gap after the last end.

## Example 1

Input:

```
20 3
2 5
4 9
12 14
```

Output:

```
6
```

## Example 2

Input:

```
10 1
0 10
```

Output:

```
0
```
