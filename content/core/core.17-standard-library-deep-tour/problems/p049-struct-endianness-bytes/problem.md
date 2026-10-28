# Trace: byte order, signedness and padding in `struct`

The same number can be stored as different bytes, and the same bytes can mean different numbers.
It depends on the **byte order** (`<` little-endian: lowest byte first; `>` big-endian: highest byte
first), on whether the code is **signed** (`h`, `i`, `q`) or **unsigned** (`H`, `I`, `Q`), and, in
native mode `@` (the default), on **alignment padding**.

`bytes.hex(" ")` shows bytes as two hex digits each, separated by spaces: `b"\x01\xff".hex(" ")` is
`'01 ff'`.

What does this program print?

```python
import struct

n = 0x12345678
print(struct.pack("<I", n).hex(" "))
print(struct.pack(">I", n).hex(" "))
print(struct.pack("<h", -2).hex(" "))
print(struct.pack(">H", 513).hex(" "))
four = b"\x01\x00\x00\x00"
print(struct.unpack("<I", four)[0], struct.unpack(">I", four)[0])
print(struct.unpack("<H", b"\xff\xff")[0], struct.unpack("<h", b"\xff\xff")[0])
data = struct.pack("<HI", 7, 258)
print(len(data), data.hex(" "))
print(struct.unpack(">HI", data))
print(struct.calcsize("<BI"), struct.calcsize("@BI"), struct.calcsize("@IB"))
print(int.from_bytes(b"\x00\x01", "big"), int.from_bytes(b"\x00\x01", "little"))
print(struct.pack("<3s", b"abcdef"), struct.pack("<5s", b"ab"))
print(struct.pack("<f", 1.0).hex(" "), struct.pack(">f", 1.0).hex(" "))
```

Facts you need:

- `I` is 4 bytes unsigned, `H` / `h` are 2 bytes (unsigned / signed), `B` is 1 byte, `f` is a
  4-byte float. Negative numbers are stored in **two's complement**: `-1` is all bits set.
- In native mode `@`, a 4-byte `I` must start at an offset that is a multiple of 4 (true on every
  common PC and phone), so padding bytes are inserted **before** it when needed. No padding is added
  at the end of the format.
- The float `1.0` is the 32-bit pattern `0x3F800000`.

Write the exact output, one line per `print`, in `answer.txt`.
