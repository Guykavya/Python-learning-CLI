## Hint 1

`re.findall` gives strings. Which function gives you `Match` objects one at a time? What does
a `Match` object know about where it was found?

## Hint 2

`m.start()`, `m.end()` and `m.span()` (both at once). An empty match is still a `Match`: do not
throw it away.

```
result = []
for each m in re.finditer(pattern, text):
    add m.span() to result
return result
```
