# Which x is it?

Predict **exactly** what this program prints. For each name inside each function, find the
**first** scope that defines it, in the order Local, Enclosing, Global, Built-in.

```python
x = "G"

def outer():
    x = "E"
    def inner():
        x = "L"
        print("inner:", x)
    inner()
    print("outer:", x)

def read_outer():
    x = "E2"
    def inner():
        print("read:", x)
    inner()

def read_global():
    print("global:", x)

def shadow():
    len = 3
    print("shadow:", len)

outer()
read_outer()
read_global()
shadow()
print("module:", x, len("abc"))
```

Write your answer in `answer.txt`, one line per printed line.
