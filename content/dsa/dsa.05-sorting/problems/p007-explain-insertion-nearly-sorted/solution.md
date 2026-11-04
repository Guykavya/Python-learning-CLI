## Approach

Relate each shift to one inversion. Then total time is `n + I`: `n` for the loop and `I` for the shifts.

## Model answer

See `answer.md`. Compare it with yours point by point.

## What to check

- The formula `T = O(n + I)` is stated.
- Sorted input has `I = 0`; reverse input has `I = n(n-1)/2`.
- An example with few inversions is given and costed.
- Small-piece use in Timsort or introsort is mentioned.
