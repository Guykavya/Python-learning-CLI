## Approach

- 2024-08: 4.2 <= 5.0 and 92.0 >= 90.0: no breach.
- 2024-09: churn 5.0 is **on** the limit (not above it); on-time 80.5 < 90: breach.
- 2024-10: churn 6.1 > 5.0: breach; on-time 90.0 is on the limit: allowed.
- 2024-11: churn 4.9 is fine; on-time 89.9 < 90: breach.

Three breaches.

## Code

```text
2024-09 on_time_pct 80.5
2024-10 churn_rate_pct 6.1
2024-11 on_time_pct 89.9
3
```

## Complexity

Not applicable (a trace problem).

## Another way

Vectorised: `(kpis["churn_rate_pct"] > 5.0) | (kpis["on_time_pct"] < 90.0)` flags the months; the loop is easier to read when every breach needs its own message.
