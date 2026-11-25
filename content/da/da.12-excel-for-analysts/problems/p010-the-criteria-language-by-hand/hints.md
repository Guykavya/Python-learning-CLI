## Hint 1

Take the criteria one at a time and go through all 8 cells for each. For `">=10"`: which cells are numbers, and which of those are at least 10? For `"N*"`: which cells are text that starts with N or n?

## Hint 2

`"<>North"` is every cell that does **not** match `North` (case-insensitive): that includes the blank cell and the numbers. `"<>"` is the non-empty cells; `"="` is the empty ones.
