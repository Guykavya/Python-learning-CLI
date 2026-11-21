# Is it worth it?

Chapter section 1.1 (the payoff formula). Before you automate a task, do the arithmetic. A script costs time to build and time to keep working (websites change, folders move), and the factor of 2 is honest: scripts take longer than planned.

```text
minutes saved  =  minutes per run  x  runs per year  x  years
cost           =  minutes to build  +  minutes to maintain per year  x  years
worth it if       minutes saved  >  2 x cost
```

## What to write

```python
def worth_it(minutes_per_run, runs_per_year, minutes_to_build, minutes_to_maintain_per_year, years=3):
    ...
    return worth, minutes_saved
```

- `worth` is a `bool`, `minutes_saved` is the number of minutes saved over `years` (not reduced by the cost).
- The comparison is **strictly** greater: at exactly `2 x cost` the answer is `False` (a tie is not worth the risk).
- Zero runs per year saves nothing and is never worth it.
- Any negative argument, or `years < 1`, raises `ValueError` (a negative time is a bug in the caller, not a number to compute with).

## Example

```python
worth_it(10, 52, 180, 60)          # weekly 10-minute report over 3 years
# (True, 1560)                     cost = 180 + 60*3 = 360, and 1560 > 720
worth_it(5, 1, 120, 60)            # a yearly 5-minute form
# (False, 15)
worth_it(10, 10, 150, 0)           # saved 300, cost 150: exactly 2 x cost
# (False, 300)
```
