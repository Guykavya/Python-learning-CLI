## Approach

- (5, 4): rule 1 -> Champions.
- (4, 3): rule 1 fails (f < 4); rule 2 (r >= 3, f >= 3) -> Loyal.
- (3, 3): rule 2 -> Loyal.
- (3, 2): no rule matches (r = 3 is neither >= 4 nor <= 2) -> Needs attention.
- (4, 2): rule 3 -> New / promising.
- (2, 3): rule 4 -> At risk.
- (2, 2): rule 5 -> Hibernating.
- (3, 1): Needs attention.

## Code

```text
(5, 4) Champions
(4, 3) Loyal
(3, 3) Loyal
(3, 2) Needs attention
(4, 2) New / promising
(2, 3) At risk
(2, 2) Hibernating
(3, 1) Needs attention
```

## Complexity

Not applicable (a trace problem).

## Another way

A lookup table with 25 cells (r from 1 to 5, f from 1 to 5) makes every case explicit and easy for a business reader to review; the `if` chain is shorter to write.
