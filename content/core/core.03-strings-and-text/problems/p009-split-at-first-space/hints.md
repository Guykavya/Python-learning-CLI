## Hint 1

You want exactly one cut, at the first space. Which method always returns three parts?

## Hint 2

`text.partition(" ")` gives `(before, separator, after)`. If there is no space, `after` is `""`.

## Hint 3

```
text = input().strip()
command, space, rest = text.partition(" ")
print("Command:", command)
print("Rest:", rest)
```
