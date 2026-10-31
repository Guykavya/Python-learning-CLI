- Using `>` instead of `>=` in the tick loop. Then `time_left` can reach 0 and the light stays on a
  colour whose time is over.
- Forgetting that `advance()` resets `time_left`, and subtracting the whole `seconds` from the new
  colour's timer.
- Changing the colour in `tick` without calling `advance()`, and forgetting the history there.
- `self._durations = durations`. The light then shares the caller's dict, or even the class's
  `DEFAULT_DURATIONS`, so a change in one place changes every light.
- Making `state` a plain attribute. Then `t.state = "purple"` is accepted silently.
- In `emergency`, always appending `"red"`. If the light was already red, nothing changed.
- `__repr__` with `{self._state}` instead of `{self._state!r}`: that prints `state=green` without quotes.
