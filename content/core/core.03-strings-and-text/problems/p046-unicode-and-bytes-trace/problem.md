# Unicode and bytes

Predict **exactly** what this program prints, one line per `print`. Do not run it until you have written your answer.

```python
s = "née"
print(len(s), len(s.encode("utf-8")))
print(s.encode("utf-8"))
print(s.upper())
print(ord(s[1]), f"{ord(s[1]):x}")
print(chr(0x41) + chr(97))
b = s.encode()
print(b[1], b[1:3])
print(b[1:3].decode())
print("ß".upper(), "ß".casefold())
ba = bytearray(b"cat")
ba[0] = ord("b")
print(ba, ba.decode())
print(b"abc" == "abc")
```

Write your answer in `answer.txt`, one line per printed line.
