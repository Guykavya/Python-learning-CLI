# Longest increasing streak

Read `n` numbers. A **streak** is a run of consecutive positions where each value is strictly
greater than the value just before it. A single value on its own is a streak of length 1.

Find the longest streak and print its length and where it starts and ends.

**Rule:** do not store the numbers. No lists (`[...]`, `list()`, `sorted()`). Read each number once,
in a single loop, and remember only what you need.

## Input

The first line is `n`. Then `n` lines follow, each with one integer. Use `input()` without a prompt
message.

## Output

Two lines:

```
length L
from S to E
```

where `L` is the length of the longest streak and `S`, `E` are its first and last positions,
counting from 1. If several streaks share the longest length, report the **earliest** one.

## Examples

Input `n = 8`, values `5 1 2 3 2 4 6 7`:

```
length 4
from 5 to 8
```

(Positions 5..8 hold 2, 4, 6, 7. The streak 1, 2, 3 at positions 2..4 has length 3.)

Input `n = 4`, values `3 3 3 3` (equal values do not continue a streak):

```
length 1
from 1 to 1
```

Input `n = 6`, values `1 2 0 5 6 1` (streaks: `1 2`, then `0 5 6`, then `1`):

```
length 3
from 3 to 5
```

## Constraints

- 1 <= n <= 100000
- Each value fits easily in a Python int (it may be negative).

## Before you code

Decide what you must remember while reading: the previous value, where the current streak started,
how long it is, and the best streak so far. Write these as variables in comments at the top of
`solution.py`. Then walk through `5 1 2 3 2 4 6 7` by hand with a table, one row per number.
