## Hint 1

Two levels of shape: the words (`["9:05"]` or `["9:05", "pm"]`), and the parts of the time
(`["9", "05"]` or `["9", "05", "00"]`). Match each with a sequence pattern.

## Hint 2

First turn the line into `time_text` and `suffix` (`""`, `"am"` or `"pm"`), or mark it invalid.
Then `match time_text.split(":"):` with `case [h, m]:` and `case [h, m, s]:`.

## Hint 3

Validate with guards or with `if`: every part `isdigit()`, `len(h)` is 1 or 2, `len(m) == 2`,
minutes and seconds `< 60`, and the hour range depends on the suffix. Then convert 12-hour
hours: `h % 12`, plus 12 for `pm`.
