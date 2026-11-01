## Hint 1

First label each class attribute of `Thing`: is `d` a data descriptor, a non-data descriptor or
a plain value? Then, for every line, ask whether it is a read, a write or a delete, and apply the
rule from the statement. Keep a box for `vars(t)` on paper. What does `Data.__set__` do with the
value: does it store it anywhere?

## Hint 2

```
d = Data()     -> data descriptor  (has __set__): wins over vars(t) for reads and writes
n = NonData()  -> non-data         : vars(t) wins if it has "n"
plain          -> plain class attribute: vars(t) wins if it has "plain"

t.d = 1               -> calls Data.__set__, which only prints (vars(t) gets nothing)
t.__dict__["d"] = 99  -> bypasses the descriptor, but reads of t.d still go to Data
del t.d               -> Data has no __delete__ ... what does Python raise?
Thing.d = "replaced"  -> the descriptor is gone from the class: what does t.d find now?
```
