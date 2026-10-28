## Approach

1. Compute the MROs with C3 (chapter section 12).
2. Trace each `super()` call as "one step to the right in the MRO of the object".

## C3 for `Bottom`, by hand

```text
L(LogMixin) = [LogMixin, object]
L(Left)     = [Left, Base, object]
L(Right)    = [Right, Base, object]

L(Bottom) = Bottom + merge([LogMixin, object], [Left, Base, object], [Right, Base, object], [LogMixin, Left, Right])
```

| step | heads tried | result |
|---|---|---|
| 1 | `LogMixin`: not in any tail -> take it | `Bottom, LogMixin` |
| 2 | `object`: in the tail of `[Left, Base, object]` -> skip. `Left`: not in any tail -> take | `..., Left` |
| 3 | `object`: still in tails -> skip. `Base`: in the tail of `[Right, Base, object]` -> skip. `Right` -> take | `..., Right` |
| 4 | `object`: in the tail of `[Base, object]` -> skip. `Base` -> take | `..., Base` |
| 5 | `object` -> take | `..., object` |

So `Bottom.__mro__` is `Bottom, LogMixin, Left, Right, Base, object`. `Base` comes after **both** of its
children: that is the point of C3 in a diamond.

`L(Other) = Other + merge([Right, Base, object], [Left, Base, object], [Right, Left])` =
`Other, Right, Left, Base, object`.

## Step by step

1. `Bottom()`: `Bottom.__init__` prints `Bottom init start`. `super().__init__()`: next after
   `Bottom` is `LogMixin`, which has no `__init__`, so `Left.__init__` runs: `Left init start`. Its
   `super()` (still `b`'s MRO) is `Right`: `Right init start`. Then `Base`: `Base init`. The calls
   return in reverse order: `Right init end`, `Left init end`, `Bottom init end`. `Base` runs once.
2. `b.hello()`: Bottom -> LogMixin -> Left -> Right -> Base, each adding its name in front ->
   `['Bottom', 'Log', 'Left', 'Right', 'Base']`. The mixin's `super().hello()` goes to `Left`
   although `LogMixin` has no parent besides `object`.
3. The MRO list -> `['Bottom', 'LogMixin', 'Left', 'Right', 'Base', 'object']`.
4. `Left.hello(b)`: starts in `Left`, but `super()` uses `b`'s MRO, where `Right` comes after `Left`
   -> `['Left', 'Right', 'Base']`.
5. `Left()`: a new object whose MRO is `Left, Base, object`. Now `super()` in `Left` is `Base`:
   `Left init start`, `Base init`, `Left init end`. `.hello()` -> `['Left', 'Base']`. The same code
   behaves differently because the object is different.
6. `Other()`: `Other` has no `__init__`, so `Right.__init__` runs first: `Right init start`; its
   `super()` in `Other`'s MRO is `Left`: `Left init start`, `Base init`, `Left init end`,
   `Right init end`. `.hello()` -> `['Right', 'Left', 'Base']`.
7. `Broken(Left, Bottom)`: `merge([Left, Base, object], [Bottom, LogMixin, Left, ...], [Left, Bottom])`.
   Head `Left` is in the tail of `L(Bottom)`; head `Bottom` is in the tail of `[Left, Bottom]`. No
   head can be taken -> `TypeError` -> `Broken: no consistent MRO`. (A class cannot come before its
   own subclass.)
8. `Mixed(Bottom, Other)`: after taking `Bottom`, `LogMixin` and `Other`, the lists are
   `[Left, Right, Base, object]` and `[Right, Left, Base, object]`. `Left` is in the tail of the second,
   `Right` in the tail of the first -> stuck -> `Mixed: no consistent MRO`. `Bottom` wants Left before
   Right, `Other` wants Right before Left.

## Output

```text
Bottom init start
Left init start
Right init start
Base init
Right init end
Left init end
Bottom init end
['Bottom', 'Log', 'Left', 'Right', 'Base']
['Bottom', 'LogMixin', 'Left', 'Right', 'Base', 'object']
['Left', 'Right', 'Base']
Left init start
Base init
Left init end
['Left', 'Base']
Right init start
Left init start
Base init
Left init end
Right init end
['Right', 'Left', 'Base']
Broken: no consistent MRO
Mixed: no consistent MRO
```

## Complexity

Not applicable.

## Another way

Check every MRO in the REPL with `Bottom.mro()` before you trace the calls. Problem p067 asks you to
write the C3 merge as a function and compare it with Python.
