# Fix the diamond that initialises its base twice

`starter.py` models office machines. A `Copier` is both a `Printer` and a `Scanner`, and both of
those are `Device`s: a **diamond**.

```text
        Device
       /      \
   Printer   Scanner
       \      /
        Copier
```

Every class calls its parent **by name**, for example `Device.__init__(self, name)`. Try it:

```python
>>> c = Copier("office", dpi=600, colour=False)
>>> Device.connections
2                       # one copier, but two connections were opened!
>>> c.log
['Device', 'Scanner', 'Copier']     # where did 'Printer' go?
```

`Printer.__init__` runs `Device.__init__`, and then `Scanner.__init__` runs it **again**. The second run
opens a second connection and replaces `self.log` with a new empty list, so the `"Printer"` entry is lost.

Rewrite the four classes in `solution.py` so that they cooperate with `super()`:

- `Device.__init__(self, name, **kwargs)`: sets `self.name`, sets `self.log = ["Device"]`, adds 1 to
  the class attribute `Device.connections`, and calls `super().__init__(**kwargs)` (so a wrong keyword
  ends in `TypeError` from `object`).
- `Printer.__init__(self, *, dpi=300, **kwargs)` and `Scanner.__init__(self, *, colour=True, **kwargs)`.
- `Copier.__init__(self, name, *, dpi=300, colour=True, copies_per_minute=20)`. It passes `name`,
  `dpi` and `colour` on as **keywords** (`name=name, dpi=dpi, colour=colour`), because the next class
  in the MRO may not be the one you think.
- `Printer.__init__` and `Scanner.__init__` must take `name` through `**kwargs` and hand it on.
  So a single printer or scanner is now created with keywords: `Printer(name="p1", dpi=1200)`.
  That is the usual price of cooperative classes.
- **Order:** every `__init__` first calls `super().__init__(...)` and only **then** sets its own
  attributes and appends its class name to `self.log`. So the log lists the classes from the base up.
- Never call a class by name (`Device.__init__(self, ...)`) inside these methods.

Keep `connections = 0` as a class attribute of `Device`. The tests set it back to 0 before each test.

## Example

```python
>>> Copier.__mro__        # Copier, Printer, Scanner, Device, object
>>> c = Copier("office", dpi=600, colour=False, copies_per_minute=30)
>>> Device.connections
1
>>> c.log
['Device', 'Scanner', 'Printer', 'Copier']
>>> (c.name, c.dpi, c.colour, c.copies_per_minute)
('office', 600, False, 30)
>>> Printer(name="p1", dpi=1200).log
['Device', 'Printer']
>>> Scanner(name="s1").colour
True
>>> Printer(name="p1", colour=False)
TypeError: ... got an unexpected keyword argument 'colour'
```

A `Printer` has no `colour`, so the keyword travels down to `object.__init__`, which refuses it.
