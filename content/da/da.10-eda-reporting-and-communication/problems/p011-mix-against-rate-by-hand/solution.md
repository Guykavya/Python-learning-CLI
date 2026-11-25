## Approach

- before = 0.020 + 0.024 = 0.044 -> 4.40; after = 0.015 + 0.045 = 0.060 -> 6.00; total change 1.60 points.
- mix: new (0.10 - 0.20) x (0.15 + 0.10) / 2 = -0.0125; old (0.90 - 0.80) x (0.05 + 0.03) / 2 = +0.0040; sum -0.0085 -> **-0.85** points.
- rate: new (0.15 - 0.10) x (0.20 + 0.10) / 2 = 0.0075; old (0.05 - 0.03) x (0.80 + 0.90) / 2 = 0.0170; sum 0.0245 -> **+2.45** points.
- -0.85 + 2.45 = 1.60: the identity holds.

The base got older (fewer new customers), which **lowered** churn by 0.85 points; the rates rose in both segments, which **raised** it by 2.45. The overall rise of 1.60 hides a bigger rise inside the segments.

## Code

```text
before 4.40  after 6.00
mix -0.85  rate 2.45  total 1.60
True
```

## Complexity

Not applicable (a trace problem).

## Another way

Weights from the **before** period only (instead of averages) also give a decomposition, but it leaves an interaction term; the averaged weights make the two parts add up exactly.
