# A pipeline of steps

Write `run_pipeline(value, *steps, collect=False)` that passes `value` through each function in
`steps`, **left to right**, and returns the final value.

If the keyword-only flag `collect` is true, return instead a list of every value along the way,
starting with the original `value`.

**Examples**

```python
run_pipeline("  Hello World ", str.strip, str.lower, str.split)
# ['hello', 'world']

run_pipeline(3, lambda n: n + 1, lambda n: n * 10)
# 40

run_pipeline(3, lambda n: n + 1, lambda n: n * 10, collect=True)
# [3, 4, 40]

run_pipeline(7)                 # 7     (no steps)
run_pipeline(7, collect=True)   # [7]
```
