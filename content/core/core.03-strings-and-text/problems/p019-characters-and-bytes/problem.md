# Characters versus bytes

Read a line of text. Print:

```
Characters: <len of the text>
UTF-8 bytes: <len of the text encoded as UTF-8>
Hex: <the UTF-8 bytes as two-digit hex numbers separated by spaces>
```

**Example**

Input:
```
café
```
Output:
```
Characters: 4
UTF-8 bytes: 5
Hex: 63 61 66 c3 a9
```

`bytes` objects have a `hex()` method. `b"\x01\xff".hex(" ")` gives `'01 ff'`.
