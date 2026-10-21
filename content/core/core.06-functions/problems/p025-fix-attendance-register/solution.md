## Approach

All three bugs are about **what a function does to objects it did not create**.

1. `register=[]` is evaluated once and shared by every call that omits it. Use `None` as the
   sentinel and create the list in the body. Test `is None`, so a caller's empty list is still
   filled.
2. `all_students.remove(...)` mutates the caller's list. Return a freshly built list instead.
3. `register.sort()` reorders the caller's list. `sorted()` returns a new list.

## Code

```python
def mark_present(name, register=None):
    """Add name to register (a new one if none is given) unless present. Return the register."""
    if register is None:
        register = []
    if name not in register:
        register.append(name)
    return register


def absent_students(all_students, register):
    """Return a NEW list of students not in register, in all_students order. Change nothing."""
    return [name for name in all_students if name not in register]


def sorted_register(register):
    """Return a NEW list of the names sorted ignoring case. The register keeps its order."""
    return sorted(register, key=str.lower)
```

## Complexity

`mark_present`: O(n) for the `in` check. `absent_students`: O(n × m) with a list register; turn
the register into a set first for O(n + m). `sorted_register`: O(n log n).

## Another way

For `absent_students`, copy first and keep the original loop: `remaining = all_students[:]`,
then remove from `remaining`. It works, but `remove` is O(n) per call; the comprehension is
clearer and faster. With a large register, `present = set(register)` makes each check O(1).
