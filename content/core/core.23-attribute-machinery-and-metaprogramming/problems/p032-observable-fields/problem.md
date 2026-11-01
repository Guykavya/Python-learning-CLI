# Observable fields with history and undo

A settings screen needs three things whenever a value changes: tell the widgets that show it
(the **observer** pattern from core.22), remember what changed, and offer **undo**. Writing that
code in every setter is repetitive. A descriptor can do it once for every field.

Copy `starter.py` to `solution.py` and write:

**`Field(default=None)`**, a data descriptor:

- It learns its name with `__set_name__` and stores each object's value in that object's
  `__dict__` under the field's name (never on the descriptor, which is shared by all objects).
- Reading through the class (`Settings.volume`) returns the descriptor itself. Reading a field
  that was never set returns the default.
- Assigning a value that is **equal** to the current one does nothing at all.
- Otherwise it stores the new value, appends `(name, old, new)` to the object's history, and
  calls every subscriber of **that object**, in subscription order, as `callback(obj, name, old, new)`.

**`Observable`**, the base class:

- `__init_subclass__` records the field names of the class in `cls._fields` (a tuple): the
  parent's fields first, then the new ones, in definition order. Find fields by scanning
  `vars(cls)` for `Field` objects (not through annotations).
- `__init__(self, **values)` sets initial values. Initial values are **not** recorded in history
  and do not notify anybody. An unknown name raises `TypeError`.

**Functions** (each object has its own subscribers and history):

| Function | Does |
|---|---|
| `fields(obj_or_cls)` | the tuple of field names |
| `subscribe(obj, callback)` | adds a subscriber, returns `callback` (so it can be used as a decorator) |
| `unsubscribe(obj, callback)` | removes it |
| `history(obj)` | a **copy** of the list of `(name, old, new)` changes, oldest first |
| `undo(obj)` | reverts the last change: removes it from history, sets the field back to `old`, notifies subscribers with `(obj, name, new, old)`, does **not** add a history entry, and returns the undone `(name, old, new)`. Returns `None` if there is nothing to undo |

**Example**

```python
class Settings(Observable):
    volume = Field(default=5)
    theme = Field(default="light")

s = Settings(theme="dark")
log = []
subscribe(s, lambda obj, name, old, new: log.append(f"{name}: {old} -> {new}"))

s.volume = 7
s.volume = 7              # same value: ignored
s.theme = "blue"
log                       # ['volume: 5 -> 7', 'theme: dark -> blue']
history(s)                # [('volume', 5, 7), ('theme', 'dark', 'blue')]
undo(s)                   # ('theme', 'dark', 'blue'); s.theme is 'dark' again
log[-1]                   # 'theme: blue -> dark'
fields(Settings)          # ('volume', 'theme')
```
