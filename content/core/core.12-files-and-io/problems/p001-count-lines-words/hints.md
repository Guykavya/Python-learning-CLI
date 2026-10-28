## Hint 1

Open the file with `with open(path, encoding="utf-8") as f:` and read it into one string. Which string methods split text into lines and into words?

## Hint 2

```
text = read whole file
lines = len(text.splitlines())
words = len(text.split())
chars = len(text)
```
Note that `split()` with no argument splits on any whitespace and ignores empty pieces.
