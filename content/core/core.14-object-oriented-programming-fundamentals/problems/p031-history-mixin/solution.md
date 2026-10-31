## Approach

**What a mixin is.** A mixin is a small class that adds one feature and is not meant to be used on
its own (chapter section 13). `Counter` *is not* a kind of history; it simply *gains* a history
feature by listing `HistoryMixin` as a base.

**No `__init__`, lazy state.** If the mixin had an `__init__`, every class using it would have to
call it (with `super().__init__()`), and a class that forgets would break. So the mixin creates
its list the first time it is needed. `vars(self)` is the object's own attribute dict
(section 9): `"_history" not in vars(self)` means "this object has no list yet". `history()` reads
the list with `.get(..., [])`, so it also works before anything was logged.

**Setting vs data.** `max_history` is a class attribute: a setting that classes can override.
`TextBox` writes `max_history = 5`, and `self.max_history` in the mixin finds the `TextBox` value
first because lookup starts at the object's class. The log itself is per-object data, so it must
be an instance attribute.

## Code

```python
class HistoryMixin:
    """Adds an action log to any class. Defines no __init__ on purpose."""

    max_history = None

    def _log(self, action, *args):
        if "_history" not in vars(self):
            self._history = []
        text = ", ".join(repr(arg) for arg in args)
        self._history.append(f"{action}({text})")
        if self.max_history is not None and len(self._history) > self.max_history:
            del self._history[: len(self._history) - self.max_history]

    def history(self):
        return list(vars(self).get("_history", []))

    def clear_history(self):
        self._history = []


class Counter(HistoryMixin):
    def __init__(self, start=0):
        self.value = start

    def increment(self, by=1):
        self.value += by
        self._log("increment", by)

    def reset(self):
        self.value = 0
        self._log("reset")


class TextBox(HistoryMixin):
    max_history = 5

    def __init__(self):
        self.text = ""

    def type(self, s):
        self.text += s
        self._log("type", s)

    def backspace(self, n=1):
        self.text = self.text[: max(len(self.text) - n, 0)]
        self._log("backspace", n)

    def clear(self):
        self.text = ""
        self._log("clear")
```

Why `max(len(self.text) - n, 0)` in `backspace`? With `n` bigger than the text, `len - n` is
negative, and a negative slice end counts from the right: `"hello"[:5 - 7]` is `"hello"[:-2]`,
which is `"hel"`, not `""`. Clamping at 0 says exactly what we mean.

## Complexity

`_log` is O(k) for k arguments (dropping one old entry from the front of a list is O(m) for a log
of m entries, but m is small). `history()` is O(m).

## Another way

`hasattr(self, "_history")` also works for the lazy check here. It is less exact: it would also
find a class attribute with that name, which is the very trap we want to avoid. A
`collections.deque(maxlen=5)` drops old entries by itself and is the tool real code would use for
a bounded log.
