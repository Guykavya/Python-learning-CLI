# Trace: bound methods, plain functions and staticmethods

`a.greet("Ben")` looks simple, but a lot happens: Python finds `greet` on the **class**, makes a
**bound method** that remembers `a`, and then calls `Greeter.greet(a, "Ben")`. This trace tests
exactly when that binding happens and when it does not.

Read the program and write what it prints in `answer.txt`, one line per printed line.

```python
class Greeter:
    greeting = "Hi"

    def __init__(self, name):
        self.name = name

    def greet(self, other):
        return f"{self.greeting} {other}, I am {self.name}"

    @staticmethod
    def shout(text):
        return text.upper() + "!"

    @classmethod
    def kind(cls):
        return cls.__name__


def wave(x):
    return f"wave({type(x).__name__})"


a = Greeter("Asha")
b = Greeter("Ben")

print(a.greet("Ben"))
print(Greeter.greet(b, "Asha"))

m = a.greet
a.name = "Asha K"
print(m("Cy"))
print(m.__self__ is a, m.__func__ is Greeter.greet)

a.wave = wave
print(a.wave("hello"))
try:
    a.wave()
except TypeError:
    print("TypeError")

Greeter.wave = wave
print(b.wave())
print(a.wave(3))
del a.wave
print(a.wave())

print(a.shout("hey"), Greeter.shout("ho"))
print(a.kind(), Greeter.kind())


class Loud(Greeter):
    greeting = "HELLO"


c = Loud("Cy")
print(c.kind(), c.shout("ok"))
print(c.greet("you"))
f = Greeter.greet
print(f(c, "me"))
print(type(a.greet).__name__, type(Greeter.greet).__name__, type(a.shout).__name__)
```

Facts you need:

- A function stored on the **class** becomes a bound method when you read it through an instance.
- A function stored in the **instance** `__dict__` is just a function. Python does not bind it.
- When a name exists both in the instance `__dict__` and on the class as a normal method, the
  instance `__dict__` wins.
- `type(x).__name__` is the name of the class of `x`, for example `"str"` or `"int"`.

## Example of the format

```python
class P:
    def hi(self):
        return "hi"

p = P()
print(p.hi(), P.hi(p))
print(type(p.hi).__name__)
```

prints

```text
hi hi
method
```
