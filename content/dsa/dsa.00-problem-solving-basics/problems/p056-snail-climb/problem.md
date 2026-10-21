# The snail in the well

A snail is at the bottom of a well that is `h` metres deep. Every day it climbs up `u` metres.
Every night it slides back down `d` metres. It starts at height 0 on the morning of day 1.

The snail escapes on the first day when its height reaches **at least** `h` during the climb. Once it
is out, it does not slide back.

Read `h`, `u` and `d`, and print the number of the day on which the snail escapes, or `never` if it
never escapes.

The numbers can be as large as 10^18, so simulating one day at a time can take far too long. You
will need a formula, and the best way to find it is to simulate small cases by hand first.

## Input

Three lines: `h`, then `u`, then `d`. Use `input()` without a prompt message.

## Output

One line: the day number (an integer), or exactly `never`.

## Examples

| h | u | d | Output | Why |
|---|---|---|---|---|
| `10` | `3` | `1` | `5` | heights at the end of days 1..5: 3, 5, 7, 9, 11 (it climbs 3 from 0, 2, 4, 6, 8) |
| `5` | `5` | `100` | `1` | it climbs out on day 1, so the big slide never happens |
| `6` | `5` | `5` | `never` | 5 up, 5 down: it is back at 0 every morning |
| `1` | `1` | `0` | `1` | |

## Constraints

- 1 <= h <= 10^18
- 1 <= u <= 10^18
- 0 <= d <= 10^18
- Time limit: 3 seconds.

## Before you code

Make a table by hand for `h = 10, u = 3, d = 1` with the columns: day, height in the morning,
height after climbing, escaped?, height after the night. Then answer as comments in `solution.py`:
when does the snail escape on day 1? When does it never escape? Otherwise, how much does it gain per
full day, and how far must it get before the final climb?
