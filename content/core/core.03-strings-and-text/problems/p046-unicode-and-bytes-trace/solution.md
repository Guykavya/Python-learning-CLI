## Walkthrough

`"née"` is `n`, `é`, `e`. UTF-8 bytes: `6e c3 a9 65`.

| Line | Output | Why |
|---|---|---|
| lengths | `3 4` | `é` is two bytes |
| encoded | `b'n\xc3\xa9e'` | bytes above 127 show as `\x` escapes |
| `upper()` | `NÉE` | works on accented letters |
| `ord(s[1])` | `233 e9` | `é` is U+00E9 |
| `chr(0x41) + chr(97)` | `Aa` | 0x41 is 65 |
| `b[1], b[1:3]` | `195 b'\xc3\xa9'` | index gives an int, slice gives bytes |
| `b[1:3].decode()` | `é` | the two bytes of `é` |
| `ß` | `SS ss` | upper gives two letters, casefold gives `ss` |
| bytearray | `bytearray(b'bat') bat` | mutable; position 0 set to 98 |
| `b"abc" == "abc"` | `False` | bytes never equal str |
