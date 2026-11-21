## Approach

```python
def budget(slo, total, failed):
    _check(slo, total, failed)
    allowed = total * (1 - slo)
    remaining = allowed - failed
    return {"allowed_failures": allowed, "remaining_failures": remaining,
            "remaining_share": 1.0 if total == 0 else remaining / allowed, "exhausted": failed > allowed}


def burn_rate(slo, total, failed):
    _check(slo, total, failed)
    if total == 0:
        return 0.0
    return round((failed / total) / (1 - slo), 9)


def burn_alerts(slo, windows):
    if "1h" not in windows or "6h" not in windows:
        raise ValueError("windows needs the keys '1h' and '6h'")
    alerts = []
    if burn_rate(slo, *windows["1h"]) >= FAST_BURN:
        alerts.append("fast-burn")
    if burn_rate(slo, *windows["6h"]) >= SLOW_BURN:
        alerts.append("slow-burn")
    return alerts
```

Why two windows: the **1-hour** rule catches a sudden outage quickly (a burn of 14.4 would spend the whole 30-day budget in about 2 days, and 2% of it in that hour); the **6-hour** rule catches the slow leak that never looks dramatic (a burn of 6 spends 5% of the budget in 6 hours). Together they page for real danger and stay quiet about noise, which is the chapter's rule: *page a human only for what is urgent, user-visible and needs action now.*

## Complexity

O(1).

## Another way

Production burn-rate alerts add a short second window to each rule (for example 5 minutes with the 1-hour rule), so that an alert stops firing soon after the problem is fixed. In PromQL the 1-hour error ratio is `sum(rate(http_requests_total{status=~"5.."}[1h])) / sum(rate(http_requests_total[1h]))`, divided by `(1 - slo)`.
