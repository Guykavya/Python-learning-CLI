# A settings file parser with line numbers

Programs often read settings from a small text file:

```text
# game settings
volume = 7
difficulty = hard

fullscreen = yes
```

Write `parse_config(lines, schema)` that turns such lines into a dict. `schema` maps every
allowed setting name to a converter function (such as `int`, `str`, or a function you write).
Process the lines in order, numbering them **from 1**, including blank and comment lines.

- After `strip()`, skip empty lines and lines starting with `#`.
- Split each other line at the **first** `=` (`str.partition`), and strip the key and the value.
- Raise `ValueError` for the **first** problem found, with a message starting `line <n>: `:
  - no `=`: `line <n>: expected 'key = value', got <stripped line !r>`
  - unknown key: `line <n>: unknown setting <key!r>; known settings: <names>`
    (`<names>`: the schema keys sorted and joined with `", "`)
  - a key that already appeared: `line <n>: <key!r> is set twice (first on line <m>)`
  - the converter raises `ValueError`: `line <n>: bad value for <key!r>: <value!r>`, raised
    **`from`** the converter's error, so its explanation is kept as the `__cause__`.
- After the last line, if any schema setting was never given, raise
  `ValueError("missing settings: <names>")` with the missing names sorted and joined with `", "`.

**Example**

```python
def yes_no(text):
    if text in ("yes", "no"):
        return text == "yes"
    raise ValueError("expected yes or no")

schema = {"volume": int, "difficulty": str, "fullscreen": yes_no}
lines = ["# game settings", "volume = 7", "difficulty = hard", "", "fullscreen = yes"]
parse_config(lines, schema)
# {'volume': 7, 'difficulty': 'hard', 'fullscreen': True}

parse_config(["volume = loud"], schema)
# ValueError: line 1: bad value for 'volume': 'loud'
#   __cause__: ValueError("invalid literal for int() with base 10: 'loud'")
```
