# Trace: bytes versus characters

A string holds characters. A file holds bytes. UTF-8 turns one into the other. Predict every line. Run it in an empty folder: it creates `demo.txt`. (The characters are `c`, `a`, `f`, `é`, a space, `₹` and `5`.)

```python
text = "café ₹5"
data = text.encode("utf-8")
print(len(text))
print(len(data))
print(data[:5])
print(list(data[3:5]))
print(data.decode("utf-8") == text)
print(len("₹".encode("utf-8")))
print("é".encode("latin-1"))

try:
    "₹".encode("latin-1")
except UnicodeEncodeError:
    print("cannot encode")

try:
    data.decode("ascii")
except UnicodeDecodeError:
    print("cannot decode")

with open("demo.txt", "w", encoding="utf-8") as f:
    f.write(text)

with open("demo.txt", "rb") as f:
    print(len(f.read()))

with open("demo.txt", encoding="utf-8") as f:
    print(len(f.read()))
```

Write exactly what the program prints, one line for each printed line, in `answer.txt`. A print of an empty string is an empty line. The program never stops with an error, so you never need to write a traceback.
