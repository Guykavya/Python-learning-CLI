## Hint 1

`case ["rect", w, h]:` matches exactly three words. `case ["rect", *_]:` after it catches every
other length of a `rect` command.

## Hint 2

Convert inside the case: `w, h = float(w), float(h)`. Then check positivity before using
the area.

## Hint 3

Keep `count` and `total`. Compute `area` in each shape case, then do the positivity check,
printing and adding in one place after the `match`.
