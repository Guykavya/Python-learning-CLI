## Hint 1

Start from the very first test (a single number). What is the simplest code? Then each next test gives one more reason to change it. Do not write ahead of the tests.

## Hint 2

`piece.split("-")` gives one bound for `"5"`, two for `"1-3"`, and `""` as a bound for `"-3"` and `"1-"`. How does `isdigit()` on each bound reject them? Use a `set` for the numbers so duplicates vanish.

## Hint 3

```
if text.strip() == "": return []
numbers = set()
for piece in text.split(","):
    bounds = piece.strip().split("-")
    if len(bounds) > 2: invalid
    each bound .strip() must be isdigit(), otherwise invalid (also catches empty pieces)
    low, high = ints (high = low when one bound)
    if low > high: reversed
    add range(low, high + 1)
return sorted(numbers)
```
