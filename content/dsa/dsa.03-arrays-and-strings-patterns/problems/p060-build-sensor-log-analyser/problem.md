# Build a sensor log analyser

Put the whole module together in one program. A sensor has logged `n` readings, one per minute (whole numbers,
never negative). Your program loads the log, then answers a list of **commands** about it, one output line per
command.

## Input

- Line 1: `n`.
- Line 2: the `n` readings `a[1] .. a[n]`.
- Line 3: `q`, the number of commands.
- Then `q` lines, one command each.

## Commands

Positions are 1-based. A "stretch" or "window" is a block of consecutive readings.

| command | output |
|---|---|
| `sum l r` | the sum of `a[l..r]` (inclusive). Needs `1 <= l <= r <= n`. |
| `best k` | the largest sum of any window of exactly `k` readings. Needs `1 <= k <= n`. |
| `maxsub b` | the largest sum of `a[i] - b` over a **non-empty** stretch: "the stretch that beats the baseline `b` by the most". Any integer `b`; the answer can be negative. |
| `longest_le S` | the length of the longest stretch whose sum is `<= S`; `0` if there is none. Any integer `S`. |
| `above k t` | how many windows of exactly `k` readings have an **average** `>= t`. Needs `1 <= k <= n`; any integer `t`. |
| `maxwin k` | the maximum of every window of `k` readings, from left to right, separated by single spaces (`n - k + 1` numbers). Needs `1 <= k <= n`. |

## Errors

Print `error` (and go on with the next command) when a line:

- is blank, or its first word is not one of the six names above (names are lower case: `SUM` is an error);
- has the wrong number of arguments;
- has an argument that is not an integer. An integer is an optional `-` followed by one or more digits: `-3` and
  `007` are fine; `1.5`, `+3`, `-`, `abc` are not;
- breaks a "Needs" rule from the table (for example `sum 5 2`, `best 0`, `maxwin 9` when `n = 8`).

## Example

Input:

```
8
3 1 4 1 5 9 2 6
10
sum 2 5
best 3
maxsub 4
longest_le 10
above 2 5
maxwin 3
sum 5 2
mean 1 2
best 0
maxsub -2
```

Output:

```
11
17
6
4
2
4 4 5 9 9 9
error
error
error
47
```

- `sum 2 5`: `1 + 4 + 1 + 5 = 11`.
- `best 3`: the window `9 2 6` has sum 17.
- `maxsub 4`: the values minus 4 are `-1 -3 0 -3 1 5 -2 2`; the best stretch is `1 5` (sum 6).
- `longest_le 10`: `3 1 4 1` has sum 9; no 5 readings in a row stay within 10.
- `above 2 5`: average at least 5 means sum at least 10: `5 9` and `9 2`.
- `maxsub -2`: every value plus 2 is positive, so the whole log wins: `31 + 8 * 2 = 47`.

## Constraints

- `1 <= n <= 200000`, `0 <= a[i] <= 10^9`
- `1 <= q <= 200000`
- At most **20** commands are not `sum`. The `sum` commands can be all 200000 of them, so each one must be O(1).
- Every other command must be O(n) (or O(n log n)): no nested loops over the log.

Use `input()` without a prompt message. Print exactly one line per command.

## Plan before you code

1. Read the log and build the prefix sums `P` **once**. Which commands can use `P`? (`sum`, `best`, `above`.)
2. Which pattern does each command need? `best` and `above`: a fixed window (or prefix differences). `maxsub`:
   Kadane on `a[i] - b`. `longest_le`: a variable window, valid because readings are never negative. `maxwin`: a
   monotonic deque.
3. Write one small function per command that takes integers and returns the output **string**. Test each one by hand
   on the example.
4. Then write the dispatcher: split the line, check the name, the argument count and that every argument is an
   integer, **before** converting. Do the range checks inside each function.
5. Edge cases to try by hand: `k = 1`, `k = n`, `longest_le -1`, `longest_le 0` with zeros in the log, `above 3 0`,
   `maxsub 1000000000`.
