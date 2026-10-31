## Approach

The bug is the classic diamond problem (chapter section 12). Calling parents by name runs **every
path** through the diamond, so `Device`, the shared base, runs once per path. The fix is cooperative
`super()`: each class calls `super().__init__`, and `super()` walks the MRO of the actual object,
`Copier -> Printer -> Scanner -> Device -> object`, visiting every class exactly once.

Three details make it work:

1. **Keywords only.** `Printer` does not know whether `super()` leads to `Scanner` or `Device`, so it
   cannot pass positional arguments. Everybody takes their own keyword and forwards `**kwargs`.
2. **super() first.** `Device` creates `self.log`, so each class calls `super().__init__` first and
   appends afterwards. The calls go down the MRO, and the appends happen on the way back up:
   `Device`, `Scanner`, `Printer`, `Copier`.
3. **Device forwards too.** `Device` passes the leftovers to `object.__init__`, which raises
   `TypeError` for anything unknown, such as `colour` on a plain `Printer`.

## Trace of `Copier("office", dpi=600, colour=False)`

```text
Copier.__init__   -> super().__init__(name="office", dpi=600, colour=False)
  Printer.__init__  takes dpi=600   -> super().__init__(name="office", colour=False)
    Scanner.__init__  takes colour=False -> super().__init__(name="office")
      Device.__init__   takes name    -> super().__init__()  (object, nothing left)
      Device: name, log = ["Device"], connections = 1
    Scanner: colour, log += "Scanner"
  Printer: dpi, log += "Printer"
Copier: copies_per_minute, log += "Copier"
```

## Code

```python
class Device:
    connections = 0  # how many times a connection was opened

    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.log = ["Device"]
        Device.connections += 1


class Printer(Device):
    def __init__(self, *, dpi=300, **kwargs):
        super().__init__(**kwargs)
        self.dpi = dpi
        self.log.append("Printer")


class Scanner(Device):
    def __init__(self, *, colour=True, **kwargs):
        super().__init__(**kwargs)
        self.colour = colour
        self.log.append("Scanner")


class Copier(Printer, Scanner):
    def __init__(self, name, *, dpi=300, colour=True, copies_per_minute=20):
        super().__init__(name=name, dpi=dpi, colour=colour)
        self.copies_per_minute = copies_per_minute
        self.log.append("Copier")
```

## Complexity

O(k) per object for k classes in the MRO: each `__init__` runs exactly once.

## Another way

You can avoid the diamond completely with composition: a `Copier` **has** a printer part and a
scanner part (`self.printer = Printer(name)`, `self.scanner = Scanner(name)`) and delegates to them.
Then nothing is shared and nothing runs twice, but a `Copier` is no longer `isinstance(c, Printer)`.
Choose cooperative inheritance when the "is-a" relation is real.
