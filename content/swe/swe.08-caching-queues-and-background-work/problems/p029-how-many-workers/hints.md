## Hint 1

If on average 10 workers are busy and you want each worker busy only 70% of the time, how many workers do you need? Write it as a division. Why does a computer give 30.000000000000004 for 21 / 0.7, where you expect 30?

## Hint 2

```text
busy = arrival * seconds
workers = max(1, ceil(round(busy / target, 9)))

drain: if backlog <= 0: 0.0
       if capacity <= arrival: inf
       else: backlog / (capacity - arrival)

admit: (503, {"Retry-After": str(retry_after)}) if queue_length >= limit else (202, {})
```
