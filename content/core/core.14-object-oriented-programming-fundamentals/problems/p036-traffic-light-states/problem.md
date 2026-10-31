# A traffic light that keeps time

A traffic light shows red, then green, then yellow, then red again, forever. Each colour stays on
for a number of seconds. Write a class `TrafficLight` in `solution.py` that keeps its state and its
timer, and that can be moved forward by hand or by letting seconds pass.

**`TrafficLight(start="red", durations=None)`**

- The cycle is `red -> green -> yellow -> red`. A class attribute `NEXT` holds this as a dict.
- `durations` maps each colour to its number of seconds. `None` means the class attribute
  `DEFAULT_DURATIONS = {"red": 30, "green": 25, "yellow": 5}`. A given dict must have exactly the
  keys `"red"`, `"green"`, `"yellow"`, each an `int` of at least 1, otherwise `ValueError`.
  Keep your own copy of it.
- `start` must be one of the three colours, otherwise `ValueError`.

**Read-only properties** (setting them raises `AttributeError`):

- `state`: the current colour.
- `time_left`: seconds until the next change. It starts at the duration of the current colour.
- `history`: a **new** list of every colour the light has shown, oldest first, starting with `start`.

**Methods**

- `advance()`: switch to the next colour at once, set `time_left` to that colour's full duration,
  add the colour to the history, and return it.
- `tick(seconds)`: let `seconds` pass (`int`, 0 or more, otherwise `ValueError`). Whenever the
  seconds left to spend are **at least** `time_left`, spend `time_left` and `advance()`. Repeat.
  Then take the remaining seconds off `time_left`. Return the list of colours entered during this
  tick (often `[]`). So `time_left` never ends at 0: reaching 0 means "change now".
- `emergency()`: switch to `"red"` at once with the full red duration. If the light was not red,
  add `"red"` to the history. If it was already red, only restart its timer.
- `__repr__` returns exactly `TrafficLight(state='green', time_left=2)` (with the real values).

**Example** (durations red 3, green 2, yellow 1)

```python
t = TrafficLight(durations={"red": 3, "green": 2, "yellow": 1})
t.state, t.time_left      # ('red', 3)
t.tick(2)                 # []                 time_left is now 1
t.tick(1)                 # ['green']          1 second reaches 0: change. time_left 2
t.tick(5)                 # ['yellow', 'red']  2 s to yellow, 1 s to red, 2 s off red's 3
t.time_left               # 1
t.history                 # ['red', 'green', 'yellow', 'red']
t.advance()               # 'green'
t                         # TrafficLight(state='green', time_left=2)
t.emergency()
t.state, t.time_left      # ('red', 3)
t.state = "green"         # AttributeError
```
