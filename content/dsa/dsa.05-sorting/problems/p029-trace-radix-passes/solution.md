## Approach

Run each pass: group by the current digit (stably), then concatenate. The result of one pass is the input of the next.

## Expected output

```text
exp 1 [170, 90, 802, 2, 24, 45, 75, 66]
exp 10 [802, 2, 24, 45, 66, 170, 75, 90]
exp 100 [2, 24, 45, 66, 75, 90, 170, 802]
done [2, 24, 45, 66, 75, 90, 170, 802]
```

## Why

Passes: ones, tens, hundreds. The tens pass keeps `802` before `2` because they were in that order after the ones pass (`802` was to the left of `2`); the hundreds pass then puts `2` (hundreds digit 0) ahead of `802` anyway, but ties in a digit are always broken by the order of the previous pass. That is the proof that LSD radix sort is correct.
