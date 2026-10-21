## Hint 1

Which method cuts at the **last** occurrence of a separator? What does it return when the separator is missing?

## Hint 2

`head, dot, tail = name.rpartition(".")`. With no dot you get `("", "", name)`. So the name is `head or tail`, and the extension is `(dot and tail)` but replaced by `(none)` when it is empty.

## Hint 3

```
name = input()
head, dot, tail = name.rpartition(".")
print("Name:", head or tail)
print("Extension:", (dot and tail).lower() or "(none)")
```
