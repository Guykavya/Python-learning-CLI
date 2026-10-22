# A hint does not fix a mutable default

mypy accepts both functions below. One of them has the mutable-default trap from core.06.
Predict **exactly** what the program prints.

```python
def add_tag(tag: str, tags: list[str] = []) -> list[str]:
    tags.append(tag)
    return tags


def add_tag_safe(tag: str, tags: list[str] | None = None) -> list[str]:
    if tags is None:
        tags = []
    tags.append(tag)
    return tags


a = add_tag("x")
b = add_tag("y")
print(a)
print(b)
print(a is b)
c = add_tag_safe("x")
d = add_tag_safe("y")
print(c)
print(d)
print(c is d)
mine: list[str] = ["m"]
e = add_tag("z", mine)
print(e)
print(mine)
print(add_tag("w"))
print(add_tag.__defaults__)
```

Write the printed lines, one per line, in order. (`__defaults__` is a tuple that Python keeps
with the function. It holds the default values, and a one-item tuple prints with a trailing comma.)

Write your answer in `answer.txt`.
