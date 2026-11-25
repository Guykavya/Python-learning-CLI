## Hint 1

For each case ask the same question: *what does the missing value mean in the real world?* Is it "unknown by accident",
"unknown and person-dependent", "nothing happened" or "there is no such thing"? Then ask what a fill would claim, and
whether that claim is true.

## Hint 2

```text
1. sensor hour:  short outage, smooth process -> interpolate short gaps only
2. income, young: MAR -> fill with the visible column that explains it + indicator + report both answers
3. product, no rows: zero in disguise (after checking the shop was open and the item stocked) -> 0
4. absent student: not applicable -> keep missing / category "absent"; never fill a target
final: show the same number under a second method
```
