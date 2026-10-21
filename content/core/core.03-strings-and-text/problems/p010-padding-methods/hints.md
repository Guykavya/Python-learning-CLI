## Hint 1

Section 15 of the chapter lists four padding methods. Which three match the three lines?

## Hint 2

`rjust` and `ljust` take a second argument: the fill character.

## Hint 3

```
code = input()
print(code.zfill(6))
print(code.rjust(8, "."))
print(code.ljust(8, ".") + "|")
```
