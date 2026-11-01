## Hint 1

Take one `print` at a time and evaluate its arguments from left to right. Write the value of
every sub-expression on paper. Watch `repr(...)`: it shows quotes around strings. Which lines
call a function whose side effect matters (`default()` and `calls`)?

## Hint 2

Key facts for the hard lines.

```
config.get("a", default())   -> default() runs BEFORE get, even though "a" exists
sorted(words, key=len)       -> keys 2,1,2,1,2 ; ties keep original order
a, b = b, a + b              -> three turns: (1,2) -> (2,3) -> (3,5) -> (5,8)
[[0] * 2] * 2                -> two references to ONE inner list
any([]) is False, all([]) is True
y += [4]                     -> changes the list in place (x too); z = x + [5] is a new list
```
