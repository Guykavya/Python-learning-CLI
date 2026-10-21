## Code

```python
text = input()
data = text.encode("utf-8")
text_rev = text[::-1]
bytes_rev = data[::-1].decode("utf-8", errors="replace")
print(f"Hex: {data.hex(' ')}")
print(f"Bytes: {len(data)}")
print(f"Text reversed: {text_rev}")
print(f"Bytes reversed: {bytes_rev}")
print(f"Same: {text_rev == bytes_rev}")
```

## What happens to `é`

`é` is `c3 a9`. Reversed, the bytes are `a9 c3`. In UTF-8, `a9` is a continuation byte with nothing before it, and `c3` is a start byte with nothing after it. Neither is valid on its own, so each becomes `�`.

## The lesson

Text operations belong on `str`, not on encoded bytes. For pure ASCII the two agree, which is exactly why this kind of bug hides until someone types a name like `José`.
