## Hint 1

Build the pattern from the end, one rule at a time, and test each step with `re.fullmatch` in the REPL. First: ten digits starting with 6-9. Then: allow an optional space or hyphen after the fifth digit. What character class is "a space or a hyphen", and which quantifier makes it optional?

## Hint 2

The prefix is **one of two** forms, and the whole prefix is optional. Use alternation inside a group: `(A|B)?`. Inside it, `+` is special in a regex (it is a quantifier), so the plus of `+91` must be written as `\+`. And remember `s.strip()` before matching.

## Hint 3

```
prefix  = (?: \+91 [ -]?  |  0 )?
number  = [6-9] [0-9]{4} [ -]? [0-9]{5}
is_mobile(s):
    return re.fullmatch(prefix + number, s.strip()) is not None
```
(Remove the spaces when you write the real pattern, or use re.VERBOSE.)
