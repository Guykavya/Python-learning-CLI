# A history mixin

Two very different classes, a `Counter` and a `TextBox`, both need the same small feature: a log
of the actions done on them. Instead of copying the code, write it once as a **mixin**: a small
class that only adds behaviour and is meant to be mixed into other classes. Write it in
`solution.py`.

**`HistoryMixin`** must **not** define `__init__` (so classes can use it without changing their own
`__init__`). It keeps the log in the instance attribute `_history`, created the first time it is
needed. It has:

- A class attribute `max_history = None`. `None` means "no limit". A class that sets it to a
  number keeps only that many newest entries.
- `_log(action, *args)` adds one entry, the text `action(arg1, arg2, ...)` where every argument is
  written with `repr()`. Examples: `increment(2)`, `type('hi')`, `reset()`.
- `history()` returns a **new** list of the entries, oldest first. It returns `[]` for an object
  that has logged nothing yet (and it must not crash then).
- `clear_history()` empties the log.

**`Counter(HistoryMixin)`**: `Counter(start=0)` sets `value`. `increment(by=1)` adds `by` and logs
`increment(by)`. `reset()` sets `value` to 0 and logs `reset()`.

**`TextBox(HistoryMixin)`**: keeps at most **5** history entries (set `max_history`). `TextBox()`
sets `text = ""`. `type(s)` adds `s` to the end and logs `type(s)`. `backspace(n=1)` removes the
last `n` characters (if `n` is bigger than the text, the text becomes empty) and logs `backspace(n)`.
`clear()` empties the text and logs `clear()`.

**Example**

```python
c = Counter(10)
c.history()        # []
c.increment()
c.increment(5)
c.reset()
c.value            # 0
c.history()        # ['increment(1)', 'increment(5)', 'reset()']

t = TextBox()
t.type("hello")
t.backspace(2)
t.text             # 'hel'
t.history()        # ["type('hello')", 'backspace(2)']
for ch in "abcd":
    t.type(ch)
t.history()        # ['backspace(2)', "type('a')", "type('b')", "type('c')", "type('d')"]
```
