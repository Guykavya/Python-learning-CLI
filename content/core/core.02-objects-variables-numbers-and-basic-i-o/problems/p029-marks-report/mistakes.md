- Using `>` where the task says "at least": 40% would fail.
- Checking only one end of a range.
- Writing `75 <= pct >= 100`. Chains are legal with any operators, so this runs, but it means
  `75 <= pct and pct >= 100`, which is not what you want.
