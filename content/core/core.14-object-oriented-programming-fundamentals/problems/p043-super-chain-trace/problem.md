# Trace: a chain of super() calls

Three classes, each one extending the one above it. Every overridden method calls the parent's
version with `super()`, some **before** they do their own work and some **after**. Read the code
and write down exactly what it prints.

```python
class Base:
    def __init__(self, name):
        print("Base init start:", name)
        self.name = name
        self.steps = []
        print("Base init end")

    def greet(self):
        self.steps.append("Base")
        return "hello from " + self.name

    def describe(self):
        return "Base"

    def run(self):
        print("run:", self.describe())


class Middle(Base):
    def __init__(self, name, level):
        print("Middle init start")
        super().__init__(name.upper())
        self.level = level
        print("Middle init end:", self.name)

    def greet(self):
        print("Middle greet before")
        self.steps.append("Middle")
        text = super().greet()
        print("Middle greet after:", text)
        return text + "!"

    def describe(self):
        return "Middle>" + super().describe()


class Top(Middle):
    def __init__(self, name):
        super().__init__(name, level=2)
        print("Top init end:", self.level)

    def greet(self):
        text = super().greet()
        self.steps.append("Top")
        print("Top greet got:", text)
        return text.replace("hello", "hi")

    def describe(self):
        return "Top>" + super().describe()


t = Top("ravi")
print(t.greet())
print(t.steps)
t.run()
print(Middle.greet(t))
print(t.steps)
m = Middle("asha", 1)
m.run()
print(Base.describe(t), m.level)
```

In `answer.txt`, write the printed output, one line per printed line.

Things to remember:

- `super().method(...)` calls the **next** class's version of the method, with the same `self`.
- Inside any method, `self.something(...)` starts the lookup at the class of the **object**, not at
  the class where the method is written.
- `Middle.greet(t)` calls `Middle`'s version directly, skipping `Top.greet`. The `super()` inside it
  still works normally.

## Example of the format

`print("x:", [1, 2], "a" + "!")` prints `x: [1, 2] a!`.
