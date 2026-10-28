## Approach

**State in private attributes, read through properties.** The light owns three changing facts:
`_state`, `_time_left` and `_history`. Outside code may read them but must not set them (a light
that jumps from red to yellow would be a bug), so each has a property with only a getter (chapter
section 8). `history` returns a copy, so even `t.history.append(...)` cannot change the real list.

**Shared, fixed data in class attributes.** The cycle `NEXT` and `DEFAULT_DURATIONS` are the same
for every light, so they live on the class (section 5). Each light copies its durations with
`dict(...)`, so changing one light's durations never touches the class attribute or another light.

**One method does the switching.** `advance()` is the only place that changes the colour in the
normal cycle. `tick` reuses it, so the history and the timer are always updated together.

**The tick loop, traced.** Durations red 3, green 2, yellow 1. Start: red, 3 left.

| call | seconds to spend | step | result |
|---|---|---|---|
| `tick(2)` | 2 | 2 >= 3? no | time_left 3 - 2 = 1, returns `[]` |
| `tick(1)` | 1 | 1 >= 1? yes: spend 1, advance to green (2 left), seconds 0 | 0 >= 2? no; time_left 2 - 0 = 2, returns `['green']` |
| `tick(5)` | 5 | 5 >= 2: spend 2, yellow (1 left), seconds 3 | |
| | 3 | 3 >= 1: spend 1, red (3 left), seconds 2 | |
| | 2 | 2 >= 3? no | time_left 3 - 2 = 1, returns `['yellow', 'red']` |

## Code

```python
class TrafficLight:
    NEXT = {"red": "green", "green": "yellow", "yellow": "red"}
    DEFAULT_DURATIONS = {"red": 30, "green": 25, "yellow": 5}

    def __init__(self, start="red", durations=None):
        if durations is None:
            durations = self.DEFAULT_DURATIONS
        if sorted(durations) != ["green", "red", "yellow"]:
            raise ValueError("durations needs exactly the keys 'red', 'green' and 'yellow'")
        for colour, seconds in durations.items():
            if not isinstance(seconds, int) or seconds < 1:
                raise ValueError(f"duration of {colour} must be a whole number of at least 1, got {seconds!r}")
        if start not in self.NEXT:
            raise ValueError(f"start must be 'red', 'green' or 'yellow', got {start!r}")
        self._durations = dict(durations)
        self._state = start
        self._time_left = self._durations[start]
        self._history = [start]

    @property
    def state(self):
        return self._state

    @property
    def time_left(self):
        return self._time_left

    @property
    def history(self):
        return list(self._history)

    def advance(self):
        self._state = self.NEXT[self._state]
        self._time_left = self._durations[self._state]
        self._history.append(self._state)
        return self._state

    def tick(self, seconds):
        if not isinstance(seconds, int) or seconds < 0:
            raise ValueError(f"seconds must be a whole number of at least 0, got {seconds!r}")
        entered = []
        while seconds >= self._time_left:
            seconds -= self._time_left
            entered.append(self.advance())
        self._time_left -= seconds
        return entered

    def emergency(self):
        if self._state != "red":
            self._state = "red"
            self._history.append("red")
        self._time_left = self._durations["red"]

    def __repr__(self):
        return f"TrafficLight(state={self._state!r}, time_left={self._time_left})"
```

`sorted(durations)` sorts the keys of the dict, so one comparison checks "exactly these three keys".

## Complexity

`advance`, `emergency` are O(1). `tick(s)` is O(number of changes), at most O(s), since each
change spends at least 1 second.

## Another way

For a very long `tick` you can skip whole cycles first: `seconds %= sum(durations)` after leaving
the current colour, then loop at most three times. (You would still need the list of entered
colours, so this only helps when you return a count instead of a list.) A bigger design makes each
colour a small state object with its own `next()` and `duration`; that is the state pattern you
will meet in a challenge problem.
