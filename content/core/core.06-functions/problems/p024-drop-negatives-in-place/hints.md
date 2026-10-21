## Hint 1

Can you build the list of survivors first, and then put them into the caller's list?

## Hint 2

`numbers = survivors` only rebinds the local name. What assignment replaces the **contents** of the existing list?

## Hint 3

```
numbers[:] = [n for n in numbers if n >= 0]
```
The slice assignment replaces every item of the existing list object.
