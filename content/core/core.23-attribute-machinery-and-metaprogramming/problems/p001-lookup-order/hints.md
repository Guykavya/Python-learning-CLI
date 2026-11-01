## Hint 1

Keep two boxes on paper: one for `vars(a)`, one for `vars(b)`, and a third for `vars(Dog)`
(only `kind` and `tricks` matter). For every line ask: is this a **read** (look in the instance
box, then the class box) or an **assignment / del** (only touch the instance box)?
What does `a.tricks.append(...)` do: is it an assignment to `a.tricks`, or a read followed by a
method call?

## Hint 2

```
read obj.x   -> if "x" in vars(obj): use it; else use the class attribute
obj.x = v    -> vars(obj)["x"] = v           (class untouched)
del obj.x    -> remove "x" from vars(obj)     (AttributeError if it is not there)
obj.lst.append(v) -> READ obj.lst (the class list), then change that one list in place
```

After `del a.kind`, the second `del a.kind` has nothing in `vars(a)` to remove, even though
`a.kind` can still be read from the class.
