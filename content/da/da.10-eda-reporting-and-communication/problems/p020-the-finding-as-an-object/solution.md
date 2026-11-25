## Approach

Every sentence that contains a number is an f-string over `R`. The fixed parts (owners, dates, limitations) are words, not numbers measured from the data.

## Code

```python
def make_finding(R):
    return Finding(
        headline=(f"Monthly churn rose from {R['churn_before']:.1f}% to {R['churn_after']:.1f}% in Sep-Dec 2024, almost entirely because "
                  f"on-time delivery fell from {R['ontime_before']:.0f}% to {R['ontime_after']:.0f}%"),
        recommendations=[{"action": f"Restore the on-time rate to {R['ontime_before']:.0f}% (review the courier contract first)",
                          "owner": "Head of Operations", "by": "31 January 2025"}],
        impact=(f"Each month of delay costs about {R['saved']:.0f} customers (range {R['saved_lo']:.0f} to {R['saved_hi']:.0f}). "
                "The cost of the fix is not yet known."),
        evidence=[f"Customers with a late box in the last 3 weeks leave {R['rr']:.1f} times as often (95% CI {R['rr_lo']:.1f} to {R['rr_hi']:.1f}).",
                  f"Late boxes account for {R['late_pts']:.1f} points (95% CI {R['late_pts_lo']:.1f} to {R['late_pts_hi']:.1f}) of the rise in monthly churn."],
        confidence="High for late deliveries as the main cause: timing, size and a stable rate ratio agree.",
        limitations=["Observational data: customers were not randomly assigned late boxes.",
                     "We do not know whether one late box or its handling drives the exit."],
        next_steps=["Operations to split late boxes by courier and city this month.",
                    f"Success measure: monthly churn back to {R['churn_before']:.1f}% within three months of the fix."],
    )
```

(The `Finding` class from the starter stays above it.)

## Complexity

O(1).

## Another way

Keep the sentences in a template file with `{placeholders}` and fill them with `str.format_map(R)`; the code stays shorter, but a typo in a placeholder only shows up when it runs.
