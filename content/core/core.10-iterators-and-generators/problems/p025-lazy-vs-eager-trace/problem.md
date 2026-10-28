# Trace: when does the work happen?

A list comprehension and a generator expression look almost the same. They do the work at very
different moments. The `print` calls inside `double` and `source` show you **when** each line
of work runs.

Predict the exact output.

```python
def double(x):
    print("double", x)
    return x * 2


def source():
    print("source called")
    return [10, 20]


a = [double(x) for x in [1, 2, 3]]
print("built a")
for v in a:
    print("got", v)

b = (double(x) for x in [1, 2, 3])
print("built b")
for v in b:
    print("got", v)
print("again", list(b))

c = (x + 1 for x in source())
print("built c")
print(next(c))
```

Write exactly what the program prints, one line for each printed line, in `answer.txt`.
The program never stops with an error, so you never need to write a traceback.
