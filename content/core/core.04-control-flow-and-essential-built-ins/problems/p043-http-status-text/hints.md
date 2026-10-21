## Hint 1

Single codes are literal patterns: `case 200:`. Several codes for one text: `case 301 | 302 | 307 | 308:`.

## Hint 2

For "any other 4xx", capture the value and add a guard: `case n if 400 <= n <= 499:`. Where must
this case go relative to `case 404:`?

## Hint 3

End with `case _:` for everything else.
