## Hint 1

`bytes` can be sliced just like `str`. What is `data[::-1]` when `data` is a bytes object?

## Hint 2

`data = text.encode("utf-8")`. Then `data[::-1].decode("utf-8", errors="replace")`. Without `errors="replace"`, the decode would raise `UnicodeDecodeError`.

## Hint 3

```
text = input()
data = text.encode("utf-8")
text_rev = text[::-1]
bytes_rev = data[::-1].decode("utf-8", errors="replace")
print("Hex:", data.hex(" "))
print("Bytes:", len(data))
print("Text reversed:", text_rev)
print("Bytes reversed:", bytes_rev)
print("Same:", text_rev == bytes_rev)
```
