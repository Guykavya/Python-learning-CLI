# Trace: Protocol or ABC, who is accepted?

An **ABC** (abstract base class) is *nominal*: a class counts only if it inherits from it. A
**Protocol** is *structural*: a class counts if it has the right members. Below, one of each.
You run the file through `python -m mypy`.

```python
from abc import ABC, abstractmethod
from typing import Protocol


class Closeable(Protocol):
    def close(self) -> None: ...


class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...


class File:
    def close(self) -> None:
        print("file closed")


class Socket:
    def close(self, force: bool) -> None:
        print("socket closed", force)


class Circle:
    def area(self) -> float:
        return 3.14


class Square(Shape):
    def area(self) -> float:
        return 4.0


class Lazy(Closeable):
    pass


class Door(Closeable):
    def close(self) -> None:
        print("door closed")


def shut(c: Closeable) -> None:
    c.close()


def draw(s: Shape) -> None:
    print(s.area())


shut(File())            # A
shut(Socket())          # B
draw(Circle())          # C
draw(Square())          # D
shut(open("log.txt"))   # E
shut(Square())          # F
shut(3)                 # G
Lazy()                  # H
Door()                  # I
shut(Door())            # J
Closeable()             # K
```

For each letter, decide whether mypy reports an error **on that line** (`error`) or accepts it
(`ok`). (`open(...)` returns a text file object. The file is never really opened, mypy does not
run the code.)

Write one line per letter, in order, in the form `A: ok` or `B: error`.

Write your answer in `answer.txt`.

**Remember**: a Protocol matches by name **and signature** of its members. Check also what
a class does when it *explicitly* inherits from a Protocol, and what you may create instances of.
