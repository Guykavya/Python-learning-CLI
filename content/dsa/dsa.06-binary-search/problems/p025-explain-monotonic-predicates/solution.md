## Approach

Check each predicate for the pattern F...FT...T (or the reverse) by listing a few values; for the real-life ones argue with "more of the resource never hurts".

## Model answer

See `answer.md`. Compare it with yours point by point.

## What to check

- 1 is `F...FT...T`, first True is 8 (64 >= 50, and 49 < 50).
- 2 is `T...TF...F`, last True is 7 (49 <= 50).
- 3 is not monotonic: 2 prime (True), 4 not (False), 5 prime (True).
- 4 is `F...FT...T`: more capacity never needs more days.
- 5 is not monotonic: 19 True, 20 False, 99 True.
- 6 is `F...FT...T`: ceil(1000/x) shrinks as x grows; first True is 40.
- 7 is not monotonic: it alternates.
- A probe in the monotonic case decides everything on one side of `mid`; without monotonicity a probe tells nothing about the other values.
