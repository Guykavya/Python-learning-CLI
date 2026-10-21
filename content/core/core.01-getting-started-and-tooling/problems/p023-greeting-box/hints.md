## Hint 1

How long is `"Hello, Asha!"`? How many dashes does the Asha box have? What is
the relationship?

## Hint 2

Store the message in a variable, compute `width = len(message) + 2` once, then
build each line from `width` with `*`.

## Hint 3

```
message = "Hello, " + name + "!"
width = len(message) + 2
border = "+" + "-" * width + "+"
empty = "|" + " " * width + "|"
print border, empty, "| " + message + " |", empty, border
```
