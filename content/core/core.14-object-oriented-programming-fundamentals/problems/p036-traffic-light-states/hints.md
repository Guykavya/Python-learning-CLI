## Hint 1

What does the light need to remember? Its colour, the seconds left, and the history. Keep them in
private attributes (`_state`, `_time_left`, `_history`) and give read access through properties
with no setter. Which part never changes between lights and so can be a class attribute?

## Hint 2

Think of `tick` as spending money. You have `seconds` to spend, and the current colour costs
`time_left`. If you can pay the whole price (`seconds >= time_left`), pay it and move to the next
colour, whose price is its full duration. When you cannot pay the whole price any more, pay what
you have: `time_left -= seconds`. Try it on paper with the example before coding.

## Hint 3

```
tick(seconds):
    check seconds is an int >= 0
    entered = []
    while seconds >= self._time_left:
        seconds -= self._time_left
        entered.append(self.advance())     # advance resets _time_left
    self._time_left -= seconds
    return entered

emergency():
    if state is not red: state = "red"; history.append("red")
    time_left = durations["red"]
```

The `while` always ends, because every duration is at least 1, so `seconds` gets smaller each time.
