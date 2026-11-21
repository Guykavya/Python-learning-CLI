# Error budgets and burn rate

Chapter sections 10.5 (alerts), 10.6 (good alerts) and 10.7 (service level objectives). An **SLO** such as "99.9% of requests succeed over 30 days" leaves an **error budget**: 0.1% of requests (or about 43 minutes of total downtime) may fail. You do not page a human for every error; you page when the budget is being **spent too fast**. The speed of spending is the **burn rate**: how many times faster than the "exactly on budget" speed the service is failing.

## What to write

```python
def budget(slo: float, total: int, failed: int) -> dict: ...
def burn_rate(slo: float, total: int, failed: int) -> float: ...
def burn_alerts(slo: float, windows: dict) -> list[str]: ...
```

For all three, `slo` must be strictly between 0 and 1 (`0.999` means 99.9%); `total` and `failed` must satisfy `0 <= failed <= total`; otherwise raise `ValueError`.

- `budget(slo, total, failed)` returns a dict:
  - `allowed_failures`: `total * (1 - slo)`;
  - `remaining_failures`: `allowed_failures - failed` (negative when the budget is overspent);
  - `remaining_share`: `remaining_failures / allowed_failures` (`1.0` when `total == 0`); `1.0` is a full budget, `0.0` is spent, below `0.0` is overspent;
  - `exhausted`: `True` when `failed > allowed_failures`.
- `burn_rate(slo, total, failed)`: `(failed / total) / (1 - slo)`, **rounded to 9 decimal places** (floats: `0.0144 / 0.001` is `14.399999999999999`, and a rule written as `>= 14.4` must still fire), and `0.0` when `total == 0`. A burn rate of 1 spends exactly the budget over the whole period; 14.4 spends 2% of a 30-day budget in one hour.
- `burn_alerts(slo, windows)`: `windows` is a dict with the keys `"1h"` and `"6h"` (otherwise `ValueError`), each a pair `(total, failed)` for the last hour and the last six hours. Return the list of triggered rules, in this order:
  - `"fast-burn"` if the 1-hour burn rate is **at least 14.4** (page: the budget will be gone in about two days at this speed, and a deploy or an outage is the likely cause);
  - `"slow-burn"` if the 6-hour burn rate is **at least 6.0** (page: a steady leak that spends 5% of the budget in six hours).
  An empty list means "do not page".

## Example

```python
budget(0.999, total=1_000_000, failed=400)
# {'allowed_failures': 1000.0, 'remaining_failures': 600.0, 'remaining_share': 0.6, 'exhausted': False}
burn_rate(0.999, 10_000, 150)          # 15.0   (1.5% failing against a 0.1% budget)
burn_alerts(0.999, {"1h": (10_000, 150), "6h": (60_000, 60)})   # ['fast-burn']
```

The rule thresholds (14.4 and 6.0) are the usual starting values for a 30-day SLO; the chapter explains the idea (alert on symptoms, spend the budget on shipping) and its tutorial alert fires at an error ratio of 5%, a much cruder rule.
