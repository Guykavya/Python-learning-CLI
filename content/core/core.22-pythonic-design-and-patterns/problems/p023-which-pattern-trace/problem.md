# Trace: strategy, observer and command together

This small program uses three patterns at once:

- **Observer**: `Counter.watchers` are callbacks called on every `set`, in the order they were added.
- **Command**: `Add` objects have `do()` and `undo()`; the program runs them from a queue and undoes them later.
- **Strategy**: `apply(strategy, x)` just calls whatever function it is given.

Remember that `undo` here is also a change of the counter, so the observers see it.

What does this program print?

```python
class Counter:
    def __init__(self):
        self.value = 0
        self.watchers = []

    def watch(self, fn):
        self.watchers.append(fn)

    def set(self, value):
        old, self.value = self.value, value
        for fn in self.watchers:
            fn(old, value)


class Add:
    def __init__(self, counter, n):
        self.counter, self.n = counter, n

    def do(self):
        self.counter.set(self.counter.value + self.n)

    def undo(self):
        self.counter.set(self.counter.value - self.n)


def double(x):
    return x * 2


def negate(x):
    return -x


def apply(strategy, x):
    return strategy(x)


counter = Counter()
counter.watch(lambda old, new: print("log:", old, "->", new))
counter.watch(lambda old, new: print("big!") if new >= 10 else None)

queue = [Add(counter, 4), Add(counter, 7), Add(counter, -2)]
done = []

for cmd in queue:
    cmd.do()
    done.append(cmd)

print("value:", counter.value)

for strategy in (double, negate, lambda x: x + 1):
    print(strategy.__name__ if strategy.__name__ != "<lambda>" else "lambda", apply(strategy, counter.value))

while len(done) > 1:
    done.pop().undo()

counter.watchers.pop(0)
done[0].undo()
print("final:", counter.value)
```

**Example**: the first command `Add(counter, 4)` runs `counter.set(0 + 4)`, so the first
watcher prints `log: 0 -> 4`. The second watcher prints nothing because `4 >= 10` is false.

Write in `answer.txt` the lines the program prints, in order.
