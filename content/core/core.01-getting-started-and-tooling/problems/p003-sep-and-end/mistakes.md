- `print(day, "/", month, "/", year)`: prints `18 / 10 / 2026` because the
  default separator space is still added between all five values.
- `end=" "` instead of `end=""`: gives `Loading... done` with a space.
- `print(day + "/" + ...)`: `TypeError`, because `+` cannot join an `int` and a `str`.
