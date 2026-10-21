## Hint 1

How many times do you need to call `input()`? In what order does the checker
type the values?

## Hint 2

`input()` returns text, so you can join it with `+`: `"Name   : " + name`.
Build the border once with `"+" + "-" * 20 + "+"`.

## Hint 3

```
name = input()
course = input()
year = input()
border = <plus, 20 dashes, plus>
print(border)
print("Name   : " + name)
... two more labels ...
print(border)
```
