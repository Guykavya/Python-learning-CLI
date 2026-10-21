**1. Immutable.** A string object can never be changed after it is made: no character can be replaced, added or removed. `name[0] = "A"` tries to change the object, so Python refuses. To get a changed version you build a **new** string and point the name at it:

```python
name = "asha"
name = "A" + name[1:]      # or name = name.capitalize()
```

The old `"asha"` object is untouched; the name `name` now labels the new `"Asha"`.

**2. Methods return new strings.** `name.upper()` builds `"ASHA"` and returns it. If you do not store it (`name = name.upper()`), the new string is thrown away and `name` still labels the old one.

**3. Benefits.**
- *Safe sharing*: if two names, or a function and its caller, refer to the same string, neither can change it behind the other's back.
- *Hashing*: a string's hash never changes, so strings can be dictionary keys and set members.
- *Reuse*: Python can safely share one object for equal strings (interning), saving memory.
- *Simpler reasoning*: a string you checked once stays valid.

**4. Why repeated `+=` is slow.** `a + b` creates a new string of length `len(a) + len(b)` and copies both into it. Building a report line by line copies the whole report-so-far on every step: 1 line, then 2, then 3, ... For n lines that is about n*n/2 line-copies. For 50,000 lines that is over a billion characters copied. `"".join(lines)` first adds up all the lengths, allocates the final string **once**, and copies each piece **once**: work proportional to the total length.

**5. The CPython shortcut.** When `s += t` runs and nothing else refers to `s`, CPython may resize the string in place instead of copying, so a quick test can look fast. But one extra reference (another name, a list holding it) disables the trick, and other Pythons (PyPy, MicroPython) do not promise it. `join` is fast everywhere, so it is the correct habit.

Key ideas to check: objects never change, names are rebound; methods return new strings; benefits (sharing, hashing, reuse); `+=` copies repeatedly (quadratic), `join` allocates once (linear); the CPython in-place optimisation is fragile.
