# Trace: where does this attribute come from?

Three places can answer an attribute read, and which ones are searched depends on **what you
read from**:

- reading from an **instance** (`c.kind`): the instance `__dict__` and the classes in
  `type(c).__mro__`. The metaclass is **not** searched.
- reading from a **class** (`Child.kind`): the classes in `Child.__mro__` first, then the
  metaclass `type(Child)` and its bases.
- assigning or deleting (`c.kind = ...`, `del c.kind`) works on the object's **own**
  `__dict__` only (no descriptors are involved in this program).

A function found on the metaclass is bound to the **class**, just as a function found on a
class is bound to the instance.

Work out, line by line, exactly what this program prints. Write one line of output per
`print` call, in order. The program is deterministic and needs no input. (Errors are printed
as their type name only, so the text does not depend on your Python version.)

```python
class Meta(type):
    kind = "meta"

    def describe(cls):
        return "class " + cls.__name__


class Base(metaclass=Meta):
    kind = "base"
    shared = []


class Child(Base):
    pass


class Plain(metaclass=Meta):
    pass


c = Child()
p = Plain()

print(Child.kind, Plain.kind)
print(Child.describe(), Meta.describe(Plain))
print(hasattr(c, "describe"), hasattr(p, "kind"), hasattr(Plain, "kind"))
try:
    p.describe()
except AttributeError as e:
    print(type(e).__name__)
print(type(c).kind, c.kind)
c.kind = "instance"
print(c.kind, type(c).kind, Child.kind)
c.shared.append(1)
print(Base.shared, "shared" in vars(c))
c.shared = [2]
print(Base.shared, c.shared, "shared" in vars(c))
del c.kind
print(c.kind)
try:
    del c.kind
except AttributeError as e:
    print(type(e).__name__)
Child.kind = "child"
print(c.kind, Base.kind, Child().kind)
del Child.kind
print(Child.kind, c.kind)
print(type(Child).__name__, type(Meta).__name__, type(c).__name__)
print("describe" in vars(Meta), "describe" in vars(Child), "kind" in vars(Child))
print(Plain.describe is Plain.describe, Plain.describe == Plain.describe)
print(Plain.describe.__self__ is Plain)
```

Write your answer in `answer.txt`, one output line per `print`.

**Example (a different program)**

```python
class M(type):
    tag = "m"

class A(metaclass=M):
    pass

print(A.tag, hasattr(A(), "tag"))
```

prints

```
m False
```
