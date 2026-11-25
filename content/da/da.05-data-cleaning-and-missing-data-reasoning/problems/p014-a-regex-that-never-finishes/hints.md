## Hint 1

In `([A-Z]+)+`, how many ways can the engine split `AAAA` into groups? What happens to that number as the string gets
longer, and what does the engine do when the match fails at the *end* of the string? Does the rule in the problem say
"one or more groups of letters" or "one block of letters"? What is the simplest pattern for the second?

## Hint 2

```text
pattern: one block of capital letters, "-", two digits, "-", two digits, "-", two digits
         [A-Z]+-[0-9]{2}-[0-9]{2}-[0-9]{2}        (no group around the letters, no quantifier on a group)
use fullmatch so that the whole text must match
return True/False
```
The rule needs no nested quantifier at all: the "+" applies once, to a single character class.
