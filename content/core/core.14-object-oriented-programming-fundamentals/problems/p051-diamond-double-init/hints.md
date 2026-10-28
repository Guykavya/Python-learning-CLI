## Hint 1

Write the MRO of `Copier`: `Copier, Printer, Scanner, Device, object`. Inside `Printer.__init__`,
when the object being built is a `Copier`, which class does `super()` lead to: `Device` or `Scanner`?
And when the object is a plain `Printer`?

## Hint 2

Because `Printer`'s `super()` can lead to `Scanner`, `Printer` cannot know which arguments the next
class needs. So it takes only `dpi` and passes **everything else** on as keywords. That is why
`Copier` sends `name=name` as a keyword: positional arguments cannot be routed safely.

Why must `super().__init__(...)` come **first** in each method? `Device` creates `self.log`;
nobody can append before it exists.

## Hint 3

```text
Device.__init__(self, name, **kwargs):
    super().__init__(**kwargs)     # object: fails if kwargs has leftovers
    self.name = name; self.log = ["Device"]; Device.connections += 1

Printer.__init__(self, *, dpi=300, **kwargs):
    super().__init__(**kwargs)
    self.dpi = dpi; self.log.append("Printer")

Scanner: the same with colour

Copier.__init__(self, name, *, dpi=300, colour=True, copies_per_minute=20):
    super().__init__(name=name, dpi=dpi, colour=colour)
    self.copies_per_minute = ...; self.log.append("Copier")
```
