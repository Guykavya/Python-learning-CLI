# Trace: when is a file closed?

A file object has a `closed` flag. Follow the flag, and what happens when a `with` block ends, even by an error. Run it in an empty folder: it creates `demo.txt`.

```python
f = open("demo.txt", "w")
print(f.closed)
f.write("hello")
f.close()
print(f.closed)

try:
    f.write("more")
except ValueError:
    print("ValueError: file is closed")

with open("demo.txt") as g:
    print(g.closed)
    first = g.read()
print(g.closed)
print(first)

try:
    with open("demo.txt") as h:
        raise RuntimeError("boom")
except RuntimeError as e:
    print("caught", e)
print(h.closed)
print(g.name)
```

Write exactly what the program prints, one line for each printed line, in `answer.txt`. A print of an empty string is an empty line. The program never stops with an error, so you never need to write a traceback.
