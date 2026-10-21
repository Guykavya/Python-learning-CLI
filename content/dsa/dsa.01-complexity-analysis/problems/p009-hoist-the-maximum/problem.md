# Stop recomputing the maximum

Read a list of scores. Print two lines:

1. how many scores are equal to the highest score;
2. how many scores are at least half of the highest score (that is, `2 * score >= highest`).

`starter.py` is correct, but it calls `max(a)` inside the loop, so a hidden O(n) loop runs `n` times.
For 100000 scores that is about two minutes. Make it fast.

## Input

- Line 1: `n`.
- Line 2: `n` integers.

## Output

Two lines, each with one integer.

## Example

Input:

```
6
40 90 45 90 10 46
```

Output:

```
2
4
```

The highest score is 90, and two scores equal it. The scores with `2 * score >= 90` are 90, 45, 90 and 46
(46 * 2 = 92). 40 (80) and 10 (20) are not.

## Constraints

- `1 <= n <= 200000`
- `0 <= score <= 10^9`

Use `input()` without a prompt message.
