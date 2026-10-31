## Hint 1

`(?=.*[A-Z])` at the start of a pattern means "somewhere ahead there is a capital", and it
consumes nothing. So after it, the engine is still at position 0. How would you add the
lower-case and the digit rules the same way?

## Hint 2

After the lookaheads, something must actually consume the password and enforce length and
"no whitespace". Which character class means "not whitespace", and how do you say "8 or more"
of it? Why is `fullmatch` safer than `^...$` here? (Try `"Abcdefg1\n"` with `$`.)

## Hint 3

```
STRONG_RE = compile( (?=.*[A-Z]) (?=.*[a-z]) (?=.*[0-9]) \S{8,} )     # no spaces in the real pattern
strong(pw): return STRONG_RE.fullmatch(pw) is not None
```
