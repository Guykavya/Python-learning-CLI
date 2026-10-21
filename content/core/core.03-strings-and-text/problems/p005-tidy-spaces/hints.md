## Hint 1

One method removes whitespace from both ends. Which one? And which method cuts a string into words, ignoring any amount of whitespace?

## Hint 2

`text.split()` with **no argument** gives the words with all the whitespace thrown away. `" ".join(...)` glues words back with one space between each.

## Hint 3

```
text = input()
print("[" + text.strip() + "]")
print("[" + " ".join(text.split()) + "]")
```
