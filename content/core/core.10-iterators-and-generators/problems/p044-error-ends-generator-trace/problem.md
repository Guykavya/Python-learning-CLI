# An error inside a generator ends it for ever

What happens to a generator when its body raises an exception? Can you call `next()` again and
get the rest? Predict the exact output.

```python
def risky(items):
    for x in items:
        print("try", x)
        yield 10 // x
    print("risky end")


def safe(items):
    for x in items:
        try:
            yield 10 // x
        except ZeroDivisionError:
            print("skip", x)
    print("safe end")


g = risky([5, 0, 2])
print(next(g))
try:
    next(g)
except ZeroDivisionError:
    print("error!")
try:
    print(next(g))
except StopIteration:
    print("g is finished")

total = 0
try:
    for v in risky([1, 0, 5]):
        total += v
except ZeroDivisionError:
    print("loop stopped, total", total)

print(list(safe([5, 0, 2])))
```

Write exactly what the program prints, one line for each printed line, in `answer.txt`.
The program does not crash, so you never need to write a traceback.

**Example of the format**: a program that prints `try 5` and then `2` gives:

```text
try 5
2
```
