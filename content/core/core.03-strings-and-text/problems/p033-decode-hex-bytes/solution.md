## Code

```python
data = bytes.fromhex(input())
text = data.decode("utf-8")
print(f"Text: {text}")
print(f"Bytes: {len(data)}")
print(f"Characters: {len(text)}")
```

## The two layers

Hex text is a way of *writing* bytes as readable digits. `bytes.fromhex` turns the digits into real bytes. Those bytes are UTF-8-encoded text, so `decode("utf-8")` turns them into a `str`. Each step undoes one layer.

## Another way

`bytes.fromhex(line).decode()` in one expression, since UTF-8 is the default.
