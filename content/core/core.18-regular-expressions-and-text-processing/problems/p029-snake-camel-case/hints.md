## Hint 1

`to_snake` is easier in two `re.sub` passes. Pass 1 handles the end of an acronym: one or more
capitals, followed by a capital and a lower-case letter. Pass 2 handles a lower-case letter or
digit followed by a capital. Write each as two groups and the replacement `r"\1_\2"`.

## Hint 2

Pass 1 is `([A-Z]+)([A-Z][a-z])`. On `HTTPServer`, what does `[A-Z]+` grab first, and why does
it give back the `S`? For `to_camel`, the replacement depends on the text (it must be
upper-cased), so a replacement string cannot do it. Use a function. How do you keep a leading
`_` from being touched? (A lookbehind can demand a letter or digit before the `_`.)

## Hint 3

```
to_snake(name):
    s = sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    s = sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    return s.lower()

to_camel(name):
    return sub(r"(?<=[a-z0-9])_([a-z0-9])", lambda m: m.group(1).upper(), name)
```
