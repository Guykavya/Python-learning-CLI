## Hint 1

First sort the patterns: for each lookbehind, count its width. `\$` is 1, `USD ` is 4, `Rs\.`
is 3. If an alternation has alternatives of different widths, or there is a `+`, the whole
pattern is a `re.error` and `findall` never runs. Which two patterns fail?

## Hint 2

For the patterns that compile, walk along the text `Rs.250 USD 40 $7 -15 5` and, at the start of
each run of digits, look back exactly the required number of characters.

```
digits runs: 250 (after "Rs."), 40 (after "USD "), 7 (after "$"), 15 (after "-"), 5 (after " ")
(?<=Rs\.|USD) -> both width 3; "USD" is followed by a space, so only 250
(?:(?<=A)|(?<=B)) -> two separate fixed-width lookbehinds: allowed
(?<!-)\b\d+ -> every run whose start is not after "-"; inside "15", \b fails before "5"
```
