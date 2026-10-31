## Hint 1

Compute the MRO of `Bottom` **first**, before you trace anything. C3 merges the MROs of the parents
and the list of parents:

```text
L(Bottom) = Bottom + merge(L(LogMixin), L(Left), L(Right), [LogMixin, Left, Right])
L(LogMixin) = [LogMixin, object]
L(Left)     = [Left, Base, object]
L(Right)    = [Right, Base, object]
```

Rule: take the first head (first item of a list) that does **not** appear in the *tail* (anything
after the first item) of any list. Remove it everywhere. Repeat.

## Hint 2

With the MRO `Bottom, LogMixin, Left, Right, Base, object`, every `super()` call moves one step to
the right in that list, starting after the class that contains the call. For `__init__`: which classes
in the list have their own `__init__`? `LogMixin` has none.

For `Left.hello(b)`: the call starts in `Left`, but the MRO is still `b`'s. What comes after `Left`?

For `Broken(Left, Bottom)`: the bases list says "Left before Bottom". What does `L(Bottom)` say about
`Bottom` and `Left`? For `Mixed`: in which order do `Bottom` and `Other` each want `Left` and `Right`?
