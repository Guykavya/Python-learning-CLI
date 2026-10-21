## Hint 1

Which default is mutable? Which default does the body change in place, and which does it only rebind?

## Hint 2

`count += 1` on an int rebinds the local name and never touches `__defaults__`. `seen.append(...)` changes the default list itself.

## Hint 3

The call with `seen=[]` uses its own new list, so it does not affect the default. The call with `seen=None`... look at the body: what does `seen or [...]` do?
