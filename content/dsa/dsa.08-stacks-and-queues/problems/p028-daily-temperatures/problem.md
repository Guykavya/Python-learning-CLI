# Daily temperatures

`temps[i]` is the temperature on day `i`. Write `daily_temperatures(temps)` that returns a list `wait`: `wait[i]` is the number of days you have to wait after day `i` until a **strictly warmer** day, or `0` if no warmer day comes.

This is "next greater element", but the answer is a **distance**, not a value (chapter section 9, "Daily temperatures"). Storing indices on the stack gives you both.

## Example

```python
>>> daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73])
[1, 1, 4, 2, 1, 1, 0, 0]
>>> daily_temperatures([30, 40, 50, 60])
[1, 1, 1, 0]
>>> daily_temperatures([60, 50, 40, 30])
[0, 0, 0, 0]
```

Day 2 (75) waits until day 6 (76): 4 days. Day 3 (71) waits until day 5 (72): 2 days.

## Constraints

- `0 <= len(temps) <= 10**5`, `30 <= temps[i] <= 100`.
- One test has 100,000 days and a time limit; the double loop needs billions of steps for it.

## Think about

Which input makes the stack hold all `n` days at once? Which input keeps it at size 1?
