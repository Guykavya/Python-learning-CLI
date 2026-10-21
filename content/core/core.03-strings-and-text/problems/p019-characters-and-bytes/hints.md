## Hint 1

How do you turn a `str` into `bytes`? Which encoding does it use if you do not say?

## Hint 2

`data = text.encode("utf-8")`. Then `len(data)` is the number of bytes and `data.hex(" ")` is the hex dump.

## Hint 3

```
text = input()
data = text.encode("utf-8")
print("Characters:", len(text))
print("UTF-8 bytes:", len(data))
print("Hex:", data.hex(" "))
```
