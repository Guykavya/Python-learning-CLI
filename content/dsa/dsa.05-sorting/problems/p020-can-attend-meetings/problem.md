# Can one person attend every meeting?

A meeting is the **half-open** interval `[start, end)`: it occupies the time from `start` up to but not including `end`.
So a meeting ending at 5 and another starting at 5 do **not** clash. Given `n` meetings in any order, print `YES` if one person can attend all of them, else `NO`.

## Input

- Line 1: `n`.
- Next `n` lines: `start end` with `start < end`.

## Output

`YES` or `NO`.

## Constraints

- `0 <= n <= 200000`
- `0 <= start < end <= 10^9`

With `n = 0` the answer is `YES`.

## Example 1

Input:

```
3
0 30
5 10
15 20
```

Output:

```
NO
```

## Example 2

Input:

```
3
7 10
2 4
4 7
```

Output:

```
YES
```
