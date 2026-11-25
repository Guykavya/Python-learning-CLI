## Hint 1

Start from the chapter's `make_finding` (section 6.3) and keep only what this `R` has. Run the linter on your result: each message names the rule your text breaks.

## Hint 2

```text
headline = f"Monthly churn rose from {R['churn_before']:.1f}% to {R['churn_after']:.1f}% ... from {R['ontime_before']:.0f}% to {R['ontime_after']:.0f}%"
impact = f"... about {R['saved']:.0f} customers (range {R['saved_lo']:.0f} to {R['saved_hi']:.0f}) ..."
evidence = [f"... {R['rr']:.1f} times as often (95% CI {R['rr_lo']:.1f} to {R['rr_hi']:.1f}) ...", f"... {R['late_pts']:.1f} points (95% CI ...) ..."]
```
