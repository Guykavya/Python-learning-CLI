## Approach

Sort, then simulate the sweep with one box for `last_end`. On a `take` the box is updated before the print, so the line shows the new value.

## Expected output

```text
order: [(1, 4), (3, 5), (0, 6), (4, 7), (5, 9), (6, 9), (8, 11), (11, 12)]
(1, 4) take  last_end=4
(3, 5) skip  last_end=4
(0, 6) skip  last_end=4
(4, 7) take  last_end=7
(5, 9) skip  last_end=7
(6, 9) skip  last_end=7
(8, 11) take  last_end=11
(11, 12) take  last_end=12
chosen: 4 [(1, 4), (4, 7), (8, 11), (11, 12)]
```

## Why

| event | `s >= last_end`? | decision | `last_end` after |
|---|---|---|---|
| (1, 4) | 1 >= -inf | take | 4 |
| (3, 5) | 3 >= 4 no | skip | 4 |
| (0, 6) | 0 >= 4 no | skip | 4 |
| (4, 7) | 4 >= 4 yes (touching) | take | 7 |
| (5, 9) | 5 >= 7 no | skip | 7 |
| (6, 9) | 6 >= 7 no | skip | 7 |
| (8, 11) | 8 >= 7 yes | take | 11 |
| (11, 12) | 11 >= 11 yes (touching) | take | 12 |

`(4, 7)` and `(11, 12)` touch the event before them. With `s > last_end` both would be skipped and the answer would be 2: `(1, 4)` and `(8, 11)`.

`(0, 6)` is skipped because it **starts** at 0, before `last_end = 4`, not because it is long. With the key `ev[0]` (earliest start), `(0, 6)` comes first and is taken; then `(6, 9)` (starts at 6) and `(11, 12)` fit, for 3 events instead of 4.

## Another way

Draw the eight events as bars on a timeline from 0 to 12, then move a vertical line along it at `last_end`. Each taken bar pushes the line to its right end; every bar whose left end is behind the line is skipped.
