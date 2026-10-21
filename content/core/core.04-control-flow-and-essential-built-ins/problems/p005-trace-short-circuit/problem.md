# Trace short-circuit operators

Predict **exactly** what this program prints. Do not run it. Remember that `and` and `or`
return one of their operands, and that `repr()` shows strings with quotes.

```python
a = 0
b = 5
s = ""
print(a and b)
print(b and a)
print(a or b)
print(s or "empty")
print(b > 3 and "big")
print(b > 9 and "big")
print(a != 0 and b / a > 1)
print(not s, not b)
print(repr(s and s[0] == "x"))
print(b or 1 / a)
print(None or 0 or "" or "last")
print(1 and 2 and 3)
```

Write your answer in `answer.txt`, one printed line per line.
