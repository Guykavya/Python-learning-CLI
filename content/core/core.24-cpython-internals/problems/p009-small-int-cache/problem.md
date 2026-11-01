# Trace: the small-int cache and interning

`==` asks "equal values?"; `is` asks "the very same object?". For most values the two answers can
differ, and CPython adds two optimisations that make `is` look surprising:

- **The small-int cache.** CPython creates the integers from **-5 to 256** once, at start-up.
  Any operation whose result is in that range (parsing, arithmetic, ...) hands back the cached
  object instead of making a new one. Outside that range every new result is a new object.
- **Interning.** `sys.intern(s)` returns one canonical string object for each distinct text:
  the first time it stores `s`, after that it returns the stored object for any equal string.

Both are **CPython implementation details**: useful to understand, never something a program
should depend on. Compare values with `==`; keep `is` for `None` and other true singletons.

To keep the answers the same on every Python from 3.11 to 3.14, the program builds its values
at run time (with `int(...)`, `float(...)`, `"".join(...)`) instead of writing them as literals,
which the compiler is allowed to share. Work out exactly what it prints. It needs no input.

```python
import sys


def main():
    a = int("100")
    b = int("100")
    print(a == b, a is b)
    c = int("1000")
    d = int("1000")
    print(c == d, c is d)
    e = int("-5")
    f = int("-6")
    print(e is int("-5"), f is int("-6"))
    g = 200 + int("56")
    h = 200 + int("57")
    print(g, g is int("256"), h, h is int("257"))
    x = float("2.5")
    y = float("2.5")
    print(x == y, x is y)
    s1 = "".join(["py", "thon!"])
    s2 = "".join(["pyt", "hon!"])
    print(s1 == s2, s1 is s2)
    t1 = sys.intern(s1)
    t2 = sys.intern(s2)
    print(t1 == s1, t1 is t2)
    big = [int("5000")] * 3
    print(big[0] is big[2], len({id(n) for n in big}))
    nums = [int(str(n)) for n in (7, 7, 700, 700)]
    print(nums[0] is nums[1], nums[2] is nums[3])


main()
```

Write your answer in `answer.txt`, one output line per `print`.

**Example (a different program)**

```python
p = int("42")
q = int("42")
r = int("4200")
s = int("4200")
print(p is q, r is s, r == s)
```

prints

```
True False True
```
