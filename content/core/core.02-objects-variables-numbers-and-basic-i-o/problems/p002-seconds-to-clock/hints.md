## Hint 1

How many seconds are in one hour? What does `total // 3600` give you, and what is left over?

## Hint 2

`divmod(a, b)` returns `(a // b, a % b)` in one step. Use it twice: once for hours, once for minutes.

## Hint 3

`f"{5:02d}"` prints `05`. Use it for minutes and seconds only.
