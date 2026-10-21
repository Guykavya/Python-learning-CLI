# Guest lists without the shared default

Write `invite(name, guests=None)` that adds `name` to a guest list and returns the list.

- If the caller passes their own list, append to **that** list (the caller wants it filled) and
  return it.
- If the caller passes nothing, start a **brand new** empty list for this call.

**Examples**

```python
invite("Asha")              # ['Asha']
invite("Ravi")              # ['Ravi']        a new list, not ['Asha', 'Ravi']
party = []
invite("Meena", party)      # ['Meena']
invite("Kiran", party)      # ['Meena', 'Kiran']
party                       # ['Meena', 'Kiran']
```

This is the mutable default trap from chapter section 8. Writing `guests=[]` in the `def`
line would make the second example return `['Asha', 'Ravi']`.
