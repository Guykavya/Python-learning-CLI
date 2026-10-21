## Approach

The damage was: correct text, encoded to UTF-8 bytes, then decoded with the wrong encoding (latin-1). latin-1 maps each byte to exactly one character, so no information was lost. Reverse both steps:

1. `encode("latin-1")` turns each garbled character back into the byte it came from. Now you have the original UTF-8 bytes.
2. `decode("utf-8")` reads those bytes correctly.

## Code

```python
garbled = input()
fixed = garbled.encode("latin-1").decode("utf-8")
print(f"Fixed: {fixed}")
print(f"Shorter by: {len(garbled) - len(fixed)}")
```

## Why it gets shorter

Each `é` was two UTF-8 bytes, shown as two characters `Ã©`. After repair it is one character again. An emoji (four bytes) shrinks by three.

## Another way, and a warning

The third-party library `ftfy` repairs mojibake automatically, including the common Windows-1252 variety. This manual fix only works when you know exactly which wrong encoding was used, and only if nothing was lost on the way.
