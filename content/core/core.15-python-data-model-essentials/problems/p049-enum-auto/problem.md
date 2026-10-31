# Enums with `auto()`, lookups and methods

An **enum** is a fixed set of named constants. It stops typos (`"satruday"`) and magic numbers
(`if day == 6`). Each member has a `name` and a `value`:

```python
from enum import Enum, auto

class Color(Enum):
    RED = auto()        # value 1
    GREEN = auto()      # value 2
```

`Color.RED` is a member; `Color(2)` finds a member by value; `Color["GREEN"]` finds one by name;
iterating `Color` gives the members in order. An enum can have methods, properties and classmethods
like any class.

Write two enums in `solution.py`:

**`Weekday`** with members `MON, TUE, WED, THU, FRI, SAT, SUN`, values from `auto()` (so 1 to 7).

- property `is_weekend`: `True` for `SAT` and `SUN`.
- classmethod `from_name(text)`: finds a member from text such as `"monday"`, `" Sat "` or `"SUN"`
  (case does not matter; spaces around are ignored; only the first three letters count). Anything
  else raises `ValueError`.
- method `next()`: the following day; after `SUN` comes `MON`.

**`Direction`** with `NORTH = "N"`, `EAST = "E"`, `SOUTH = "S"`, `WEST = "W"` and a method
`opposite()` (NORTH and SOUTH are opposites, EAST and WEST too).

**Example**

```python
Weekday.WED.value              # 3
Weekday(6)                     # <Weekday.SAT: 6>
Weekday.from_name("friday")    # <Weekday.FRI: 5>
Weekday.SUN.next()             # <Weekday.MON: 1>
Direction("E").opposite()      # <Direction.WEST: 'W'>
```
