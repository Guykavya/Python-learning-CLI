## Hint 1

A named group is written `(?P<name>pattern)`. If your pattern has groups named `key` and
`value`, what does `m.groupdict()` return? Which function makes sure the **whole** line fits?

## Hint 2

The key is `[A-Za-z_]\w*`. For the value, `.*` would also swallow the trailing spaces. How do
you make it stop as early as possible, so a final `\s*` can take the spaces? (Think `*?`.)
Why does the value still stop at the end of the line rather than right away?

## Hint 3

```
pattern = \s*(?P<key>[A-Za-z_]\w*)\s*=\s*(?P<value>.*?)\s*
m = fullmatch(pattern, line)
return m.groupdict() if m else None
```
