## Approach

A slice with step -1 walks from the end to the start. `==` compares two strings character by character and gives a `bool`.

## Code

```python
text = input()
backwards = text[::-1]
print(backwards)
print(text == backwards)
```

## Why no `if` is needed

`text == backwards` is already the value `True` or `False`. Printing it prints the word. You only need `if` when you want to *do* different things, not when you want to show a yes/no answer.

## Another way

`"".join(reversed(text))` also reverses a string. `reversed()` gives the characters one by one from the end, and `join` glues them. The slice is shorter and faster.
