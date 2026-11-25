## Approach

- Python: `0.12 2 1.0 2.67`.
- Excel-like: `0.13 3.0 1.01 2.68`.
- The sum of the rounded lines is 4 x 10.00 = `40.00`; the rounded sum is round(40.016) = `40.02`.

The rounding rule is the first difference (0.125 and 2.5 are true halves: even against away from zero); the second is the representation (1.005 and 2.675 are only halves for a program that looks at 15 digits). The third difference is **when** you round.

## Code

```text
0.12 2 1.0 2.67
0.13 3.0 1.01 2.68
40.00
40.02
```

## Complexity

Not applicable (a trace problem).

## Another way

State the rule in the report: "totals are the sum of unrounded values, displayed to two decimals", and add a **rounding line** when a table of rounded rows must add up to a rounded total.
