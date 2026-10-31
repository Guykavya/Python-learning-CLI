## Hint 1

`takewhile(test, it)` yields items while `test` is true. What happens to the **first item**
for which `test` is false? Is it lost, or given back?

## Hint 2

If you call `iter(lines)` once and give the same iterator to `takewhile`, then after
`takewhile` stops, where is the iterator? What is left in it?

## Hint 3

```
it = iter(lines)
headers = {}
for line in takewhile(lambda line: line.strip() != "", it):
    key, value = line.split(":", 1)
    headers[key.strip()] = value.strip()
body = list(it)
return headers, body
```
