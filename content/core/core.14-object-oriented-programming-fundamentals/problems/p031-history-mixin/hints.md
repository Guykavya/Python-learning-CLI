## Hint 1

The mixin has no `__init__`, so nobody creates `self._history` in advance. Where is the first
moment you really need the list? How can you ask "does this object already have its own
`_history`?" Think of `vars(self)`, which is the object's own attribute dict.

## Hint 2

Why not `_history = []` in the mixin's class body? Section 5 of the chapter shows the shared mutable
class attribute trap. For `max_history`, though, a class attribute is exactly right: it is a
setting, not data that changes. `TextBox` overrides it with its own class attribute.

## Hint 3

```
_log(action, *args):
    if "_history" not in vars(self): self._history = []
    text = ", ".join(repr(a) for a in args)
    self._history.append(f"{action}({text})")
    if self.max_history is not None and len(self._history) > self.max_history:
        delete the oldest extra entries from the front

history():
    return a new list: list(vars(self).get("_history", []))
```
