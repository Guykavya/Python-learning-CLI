## Hint 1

Put the accepted words in two tuples. After cleaning the text, which test tells you whether it is
in a tuple?

## Hint 2

The type check must come first: `None.strip()` would raise `AttributeError`, which is not what the
problem asks for. Why does `parse_yes_no(1)` need the check too, even though `1` means yes?

## Hint 3

```
if not isinstance(text, str): raise TypeError(...)
word = text.strip().lower()
if word in YES: return True
if word in NO: return False
raise ValueError(f"... got {text!r}")
```
