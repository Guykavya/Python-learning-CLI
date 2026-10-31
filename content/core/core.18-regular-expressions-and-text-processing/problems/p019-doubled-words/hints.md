## Hint 1

Capture one word with `(\w+)`. How do you say "then some whitespace, then exactly that same
text again"? Inside the pattern, group 1's text is written `\1` (use a raw string!).

## Hint 2

Try your pattern on `"this is"` and `"the theory"`. Where does the match start or stop in the
middle of a word? Which anchor marks the edge of a word, and do you need it at the start, at
the end, or both? How do you make `\1` ignore case?

## Hint 3

```
pattern = \b(\w+)\s+\1\b      with re.IGNORECASE
result = []
for each match m in finditer(pattern, text):
    append m.group(1)
return result
```
