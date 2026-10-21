## Hint 1

Two steps: hex text to `bytes`, then `bytes` to `str`. Which class method makes bytes from hex?

## Hint 2

`data = bytes.fromhex(line)` (spaces between pairs are allowed). Then `data.decode("utf-8")`.

## Hint 3

```
data = bytes.fromhex(input())
text = data.decode("utf-8")
print("Text:", text)
print("Bytes:", len(data))
print("Characters:", len(text))
```
