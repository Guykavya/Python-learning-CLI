# Trace: where does the attribute come from?

When you write `obj.x`, Python first looks in the object's own `__dict__` (its instance
attributes) and then in the class. When you write `obj.x = value`, Python **always** writes into
the object's own `__dict__`; it never changes the class. `vars(obj)` returns that `__dict__`.

Work out, line by line, exactly what this program prints. Write one line per `print` call, with
the same spacing and quotes that `print` would give. The program needs no input.

```python
class Dog:
    kind = "canine"
    tricks = []

    def __init__(self, name):
        self.name = name


a = Dog("Rex")
b = Dog("Fido")
print(a.kind, b.kind)
a.kind = "wolf"
print(a.kind, b.kind, Dog.kind)
print(vars(a))
del a.kind
print(a.kind, vars(a))
a.tricks.append("sit")
print(b.tricks, Dog.tricks)
b.tricks = ["roll"]
print(a.tricks, b.tricks, Dog.tricks)
print(sorted(vars(b)))
Dog.kind = "dog"
print(a.kind, b.kind)
print("kind" in vars(a), "kind" in vars(Dog))
try:
    del a.kind
except AttributeError as e:
    print(type(e).__name__)
print(hasattr(a, "tricks"), "tricks" in vars(a))
```

Write your answer in `answer.txt`, one output line per `print`.

**Example (a different program)**

```python
class A:
    x = 1

a = A()
a.x = 2
print(a.x, A.x)
```

prints

```
2 1
```
