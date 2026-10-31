# throw, close and finally in a worker generator

A generator can get three kinds of messages from outside:

- `g.send(value)`: the paused `yield` gives back `value`.
- `g.throw(exc)`: the paused `yield` **raises** `exc` inside the generator.
- `g.close()`: the paused `yield` raises `GeneratorExit` inside the generator.

Predict the exact output of this program.

```python
def worker():
    print("open")
    try:
        while True:
            try:
                job = yield
                print("job", job)
            except ValueError as e:
                print("bad job:", e)
    finally:
        print("cleanup")


w = worker()
print("made")
next(w)
w.send("a")
print(w.throw(ValueError("oops")))
w.send("b")
w.close()
print("closed")
w.close()
try:
    w.send("c")
except StopIteration:
    print("dead")

w2 = worker()
w2.close()
print("never started")
```

Write exactly what the program prints, one line for each printed line, in `answer.txt`.
The program does not crash, so you never need to write a traceback.

**Example of the format** (for a different program): if a program prints `start` and then `1`, your
`answer.txt` is

```text
start
1
```

Questions to keep in mind:

1. `w.throw(...)` returns something. What, and why?
2. Which line runs when `w.close()` is called? Does `bad job:` print for it?
3. Does `w2.close()` print `open` or `cleanup`?
