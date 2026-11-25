## Approach

Chain three `.str` methods: `strip` removes outer whitespace, `replace(r"\s+", " ", regex=True)` turns every run of whitespace into a single space, and `title` capitalises each word. `.str` methods skip missing values, so they stay missing, and the index is carried along unchanged.

## Code

```python
def tidy_names(s):
    return s.str.strip().str.replace(r"\s+", " ", regex=True).str.title()
```

## Complexity

O(total number of characters), one vectorised pass per step.

## Another way

`s.str.split().str.join(" ")` also collapses whitespace (split on any run, join with one space), and missing values stay missing. `title()` has quirks: `"o'neil"` becomes `"O'Neil"` and `"van der berg"` becomes `"Van Der Berg"`; for real names you may prefer a lookup table of exceptions.
