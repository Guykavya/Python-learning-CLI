# Trace: how many times does it run?

`timeit` runs two pieces of code:

- `setup` runs **once per timing** (once per `timeit()` call, and once per batch in `repeat()`).
  It is not timed.
- `stmt` runs `number` times inside the timed loop.

`repeat(repeat=r, number=n)` is simply `r` calls of `timeit(number=n)`. Both `stmt` and `setup`
can be functions or strings of code; a string runs in its own namespace unless you pass
`globals=`. While the timed loop runs, `timeit` switches the garbage collector off and turns it
back on afterwards.

The program below uses counters instead of real timings, so its output is the same on every
machine. What does it print?

```python
import gc
import timeit

log = {"setup": 0, "stmt": 0}


def setup():
    log["setup"] += 1


def stmt():
    log["stmt"] += 1


t = timeit.Timer(stmt=stmt, setup=setup)
t.timeit(number=5)
print(log["setup"], log["stmt"])

times = t.repeat(repeat=3, number=4)
print(len(times), log["setup"], log["stmt"])

t.timeit(number=0)
print(log["setup"], log["stmt"])

data = []
timeit.timeit("data.append(len(data))", setup="data.clear()", number=3, globals=globals())
print(data)

timeit.repeat("data.append(len(data))", setup="data.clear()", repeat=2, number=2, globals=globals())
print(data)

seen = []
timeit.timeit(lambda: seen.append(gc.isenabled()), number=2)
timeit.timeit(lambda: seen.append(gc.isenabled()), setup="gc.enable()", number=1, globals=globals())
print(seen, gc.isenabled())

result = timeit.timeit(stmt, number=2)
print(type(result).__name__, log["stmt"])
```

Write in `answer.txt` the lines the program prints, in order, one per line. Save it as `demo.py`
and run it to check yourself afterwards.

**Example of the format** (for a different program): if a program runs `print(1, 5)` and then
`print([0, 1])`, the answer file is

```text
1 5
[0, 1]
```
