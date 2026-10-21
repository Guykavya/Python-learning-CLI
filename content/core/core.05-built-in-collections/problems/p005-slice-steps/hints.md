## Hint 1

A slice `words[start:stop:step]` has three parts, all optional. Which step gives every second item?

## Hint 2

`words[::2]`, `words[1::2]`, `words[::-1]`, `words[-3:]`, `words[1:-1]`.

## Hint 3

Build each line as `"Label: " + " ".join(part)`, or use `print("Label:", " ".join(part))` and
let the checker ignore the trailing space.
