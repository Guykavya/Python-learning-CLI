## Hint 1

Make two columns for each print: what Python calls on the object itself, and what it calls for items inside a container. Items inside containers always use `repr`.

## Hint 2

```
print(item)        -> str(item)   -> __str__
print([item])      -> list's own repr, item shown with repr
print(f"{item!r}")  -> repr
print(Plain())     -> no __str__ -> falls back to __repr__
```
