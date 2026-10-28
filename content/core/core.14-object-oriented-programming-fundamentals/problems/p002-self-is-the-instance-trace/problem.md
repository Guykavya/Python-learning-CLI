# Trace: self is the instance

Every method call passes the object **before the dot** as `self`. So `a.tick(5)` changes `a`, and
`b.tick()` changes `b`. Read the program and work out what it prints.

```python
class Counter:
    def __init__(self, name, start=0):
        self.name = name
        self.count = start

    def tick(self, steps=1):
        self.count += steps
        return self.count

    def reset(self):
        self.count = 0

    def show(self):
        print(self.name, "=", self.count)


a = Counter("a")
b = Counter("b", 10)
a.tick()
a.tick(5)
print(b.tick())
b.show()
a.show()

c = a
c.tick(100)
a.show()
print(c is a, b is a)

Counter.tick(b, 2)
b.show()
b.reset()
print(a.count, b.count, c.count)

r = a.tick
r()
print(a.count)
print(a.name, c.name)
```

Write every printed line in `answer.txt`, one per line.

Facts you need:

- `print(x, "=", y)` puts one space between the items: `print("z", "=", 3)` prints `z = 3`.
- `c = a` does **not** copy the object. Both names point to the same object.
- `Counter.tick(b, 2)` calls the function stored in the class and passes `b` as `self` by hand.
- `r = a.tick` (no brackets) does not call the method. It keeps a *bound method*: the function
  together with the object `a`. Calling `r()` later is the same as `a.tick()`.

## Example of the format

```python
p = Counter("p", 3)
p.tick(2)
p.show()
```

prints

```text
p = 5
```
