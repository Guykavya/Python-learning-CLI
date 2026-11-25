## Hint 1

Where would you keep "unit -> factor" so that adding a new unit means adding one line? What does a dictionary
lookup do for a key that is not there, and how could you turn that into a clear error? Think about what to do with the
spelling of the unit before you look it up.

## Hint 2

```text
FACTORS = {"g": 0.001, "kg": 1.0, "lb": 0.45359237}
for each (value, unit) pair (zip):
    key = unit stripped, lower case
    if key not in FACTORS: raise ValueError(message containing the unit)
    if value is missing: append nan
    else append value * FACTORS[key]
```
A missing value is the only number that is not equal to itself: `value != value`.
