# Fix: logins per day are too low

**This code has a bug. Find it and fix it.**

Your team counts how many logins happen each day. Each log line starts with the date:

```text
2026-10-05 login ann
2026-10-06 login bob
```

The function `count_by_day(lines)` in `starter.py` should return a dict `{date: number of lines}`.
It also skips blank lines. A teammate wrote it with a generator pipeline and `groupby`.
It passed their test, but the manager reports:

> "The dashboard says Monday 5 October had **1** login. The server says there were **3**."

The logs come from two servers and are **merged**, so the dates are not in order.

1. Run the tests and read the failing message.
2. Find the line that causes the wrong count, and explain the bug to yourself in one sentence.
3. Fix it. Keep the function's name and what it returns.

**Example**

```python
lines = [
    "2026-10-05 login ann",
    "2026-10-06 login bob",
    "",
    "2026-10-05 login cy",
    "2026-10-05 login dev",
]
count_by_day(lines)   # {'2026-10-05': 3, '2026-10-06': 1}
```
