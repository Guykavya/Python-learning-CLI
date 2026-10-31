## Hint 1

Read the pattern as a sentence, one named group at a time. For each alternation like
`0[1-9]|1[0-2]`, list the smallest and largest value it allows. For each `(...)?`, ask: what if
this part is missing, and what must come right after it?

## Hint 2

For the eight inputs, walk left to right and stop at the first character that the pattern
cannot accept. Remember three facts: in verbose mode plain spaces vanish, `$` allows a trailing
newline while `\Z` does not, and a regex compares characters, not numbers or calendars.

```
for each input:
    date part ok?  separator ok?  hour/minute ok?
    optional ":ss" -> optional ".f" only after it
    optional tz glued to the time
    end of string exactly?
```
