## Hint 1

One method removes an exact piece once. Another removes any number of chosen characters from the left.

## Hint 2

`removeprefix("#")` removes a single `#` if the text starts with it. `lstrip("#")` keeps removing `#` while there is one at the start.

## Hint 3

```
tag = input()
print("Once:", tag.removeprefix("#"))
print("All:", tag.lstrip("#"))
```
