## Code

```python
text = input()
data = text.encode("utf-8")
print(f"Characters: {len(text)}")
print(f"UTF-8 bytes: {len(data)}")
print(f"Hex: {data.hex(' ')}")
```

## What the numbers mean

`len(text)` counts code points. `len(data)` counts bytes. In UTF-8, ASCII characters take 1 byte, `é` takes 2, `₹` takes 3, and emoji take 4. So the two numbers are equal only for plain ASCII text.

## Another way

`" ".join(f"{b:02x}" for b in data)` builds the same hex text with a loop; you will learn that form later. `hex(" ")` is simpler.
