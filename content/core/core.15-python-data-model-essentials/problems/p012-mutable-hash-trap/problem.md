# Trace: the object lost in the set

A hash decides where an object is stored. What if the data the hash is built from **changes**
after the object is in a set? Trace the program.

```python
class Tag:
    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return isinstance(other, Tag) and self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return f"Tag({self.name!r})"


t = Tag("a")
s = {t}
print(t in s)
t.name = "b"
print(t in s)
print(Tag("a") in s)
print(Tag("b") in s)
print(len(s))
print(list(s))
print(any(x is t for x in s))
s = {x for x in s}
print(t in s, len(s))
```

Write every printed line in `answer.txt`, one per line.

Facts you need:

- A set stores each element's hash when it is added and never recomputes it.
- Looking up `x in s` computes `hash(x)` **now**, jumps to that bucket, and compares stored
  entries with `==` only if the stored hash equals the new hash.
- Two different strings have different hashes (assume no collisions).
- `list(s)` and `for x in s` walk over every stored element without hashing anything.

## Example of the format

```python
t = Tag("x")
print(t.name, len(set([t])))
```

prints (for the class below)

```text
x 1
```
