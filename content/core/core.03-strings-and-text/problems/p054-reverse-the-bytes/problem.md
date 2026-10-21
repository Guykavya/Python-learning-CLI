# Reverse text or reverse bytes?

Reversing a `str` reverses code points. Reversing its UTF-8 **bytes** is a different thing, and it breaks every character that uses more than one byte. Read a line and show both:

```
Hex: <the UTF-8 bytes as hex, separated by spaces>
Bytes: <number of bytes>
Text reversed: <the string reversed>
Bytes reversed: <the bytes reversed, decoded as UTF-8 with errors="replace">
Same: <True if the last two lines are equal>
```

**Example**

Input:
```
café
```
Output:
```
Hex: 63 61 66 c3 a9
Bytes: 5
Text reversed: éfac
Bytes reversed: ��fac
Same: False
```

The `�` (U+FFFD, the replacement character) appears wherever the decoder met bytes that are not valid UTF-8.
