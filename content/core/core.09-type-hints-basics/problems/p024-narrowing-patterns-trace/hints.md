## Hint 1

For each marked line, write down the type of the variable **at that line**, after all the checks above it on the path. Is `None` still possible?

## Hint 2

`continue` leaves the current loop pass, just like `return` leaves a function: after `if v is None: continue`, the rest of that pass has a `str`. A comprehension condition `if v is not None` narrows the item used on its left. But `return [v for v in values]` keeps the `None` in the items.

## Hint 3

`key in table` tells *you* the key exists, but `table.get(key)` is still typed `str | None` for mypy. In `pick`, the early `return ""` handles "both None", but mypy does not remember that fact when it reaches `return b`. And `parse(text) + 1`: what is the type of `parse(text)`?
