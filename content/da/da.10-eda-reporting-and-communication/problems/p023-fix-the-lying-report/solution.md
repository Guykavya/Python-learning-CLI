## Approach

Each fault is one place in the code. The typed numbers become `R` lookups; the interval uses the estimate's format; the limitations are copied whole. A report built only from `R` cannot disagree with the analysis, and a long list of limitations is a reason to rewrite, never to cut silently.

## Code

```python
def build_report(R):
    return Finding(
        headline=f"Monthly churn rose from {R['churn_before']:.1f}% to {R['churn_after']:.1f}% in Sep-Dec 2024, mainly because of late deliveries",
        recommendations=[{"action": "Restore on-time delivery (courier contract review)", "owner": "Head of Operations", "by": "31 January 2025"}],
        impact=f"Fixing it keeps about {R['saved']:.0f} customers (range {R['saved_lo']:.0f} to {R['saved_hi']:.0f}) a month.",
        evidence=[f"Customers with a recent late box leave {R['rr']:.1f} times as often (95% CI {R['rr_lo']:.1f} to {R['rr_hi']:.1f}).",
                  f"On-time delivery fell from {R['ontime_before']:.0f}% to {R['ontime_after']:.0f}% in the same month."],
        confidence="High for the main cause; the price effect is uncertain.",
        limitations=list(R["limitations"]),
        next_steps=[f"Success measure: monthly churn back to {R['churn_before']:.1f}% within three months."],
    )
```

## Complexity

O(number of limitations).

## Another way

Add a test that rebuilds the report from a second, very different `R` and checks that no number of the first `R` survives: it catches every typed number at once.
