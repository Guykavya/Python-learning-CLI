## Hint 1

For every read, first ask: "am I reading from an instance or from a class?" Then list the
places searched, in order, and stop at the first hit:

```
instance c:   vars(c) -> Child -> Base -> object          (never Meta)
class Child:  Child -> Base -> object -> Meta -> type
class Plain:  Plain -> object -> Meta -> type
```

Assignments and `del` touch only the dict of the object on the left of the dot.

## Hint 2

Key moments:

```
c.shared.append(1)   -> READ c.shared (finds Base.shared), then change that list in place
c.shared = [2]       -> WRITE: a new entry in vars(c); Base.shared is untouched
del c.kind (twice)   -> the first removes vars(c)['kind']; the second finds nothing in vars(c)
Child.kind = "child" -> new entry in vars(Child), shadows Base.kind for Child and its instances
Plain.describe       -> a new bound method each time (is: False), but equal (==: True)
```
