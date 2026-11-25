## Hint 1

Read every f-string in `build_report`: which numbers are not inside `{...}`? Then compare the format specs of the estimate and of its interval. Finally, look at how `limitations` is filled.

## Hint 2

```text
headline: f"... from {R['churn_before']:.1f}% to {R['churn_after']:.1f}% ..."
impact:   f"about {R['saved']:.0f} customers (range {R['saved_lo']:.0f} to {R['saved_hi']:.0f})"
evidence: {R['rr_lo']:.1f} and {R['rr_hi']:.1f}
limitations=list(R["limitations"])
```
