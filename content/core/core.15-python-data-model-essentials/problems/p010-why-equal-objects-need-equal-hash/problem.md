# Explain: why equal objects need equal hashes

Mia wrote a `Version` class that treats `"1.0"` and `"1.00"` as the same version:

```python
class Version:
    def __init__(self, text):
        self.text = text
        self.parts = tuple(int(p) for p in text.split("."))

    def __eq__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return self.parts == other.parts

    def __hash__(self):
        return hash(self.text)          # <-- Mia's line


seen = {Version("1.0")}
print(Version("1.0") == Version("1.00"))   # True
print(Version("1.00") in seen)              # False !?
```

"They are equal, so why does `in` say `False`?"

In `answer.md` (about 150 to 300 words), explain:

1. The rule that connects `__eq__` and `__hash__`. Is the rule symmetric (does a equal hash force equality)?
2. In plain words, how a dict or set uses the hash and `==` when you look up a key.
3. Exactly why Mia's `Version` breaks that rule, and what `len({Version("1.0"), Version("1.00")})` gives.
4. A one-line fix for `__hash__`, and the general principle behind it.
5. Why Python sets `__hash__ = None` when you define `__eq__` without `__hash__`.

## Example of the level of detail

"A hash is a number that works like a shelf number: the dict goes to that shelf first and only then
compares items on it with `==`." A good answer continues like this for each point.
