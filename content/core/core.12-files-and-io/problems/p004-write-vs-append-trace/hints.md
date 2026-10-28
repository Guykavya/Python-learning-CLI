## Hint 1

Keep a note of what the file contains after each `with` block. Which block uses `"w"` and so throws the old text away?

## Hint 2

After the `"w"` block with `four`, the file is just `four`. Then `!!` is appended. What does `write` return? Then `read(2)` moves the position by 2 characters, and `readline` continues from there.
