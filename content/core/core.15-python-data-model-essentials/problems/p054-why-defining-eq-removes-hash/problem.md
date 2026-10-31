# Explain: why defining `__eq__` removes `__hash__`

This is the explain assessment of the module. Study the program and its output.

```python
class A:
    def __init__(self, n):
        self.n = n

    def __eq__(self, other):
        return isinstance(other, A) and self.n == other.n


class B:
    def __init__(self, n):
        self.n = n


print(A(1) == A(1), B(1) == B(1))
try:
    print(hash(A(1)))
except TypeError as err:
    print("TypeError:", err)
print(A.__hash__, type(hash(B(1))).__name__)
try:
    {A(1): "x"}
except TypeError:
    print("A cannot be a dict key")
print({B(1), B(1)} == {B(1)}, len({B(1), B(1)}))


class C(A):
    def __hash__(self):
        return hash(self.n)


print(len({C(1), C(1)}), hash(C(5)) == hash(5))
```

Output:

```text
True False
TypeError: unhashable type: 'A'
None int
A cannot be a dict key
False 2
1 True
```

In `answer.md` (about 250 to 400 words, plus a short code block), explain:

1. **What happens.** For `A`, `B` and `C`: which are hashable, and why? What is `A.__hash__`?
2. **Why Python does this.** State the rule that equal objects must follow, and explain what would go
   wrong in a `set` or `dict` if Python kept the default hash for a class that defines `__eq__`.
3. **Three ways to get hashing back.** Show a correct `__hash__` for `A`, and name two other ways.
   Which fields may be used in the hash?
4. **The trap.** What happens if an object is hashed using a field that changes after the object was
   put in a set?
