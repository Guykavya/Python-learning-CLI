**Definitions.** A mutable object can be changed in place after it is created; its identity
stays the same while its value changes. An immutable object can never change; any "change"
produces a new object. Immutable types so far: `int`, `float`, `complex`, `bool`, `str`,
`NoneType`, `Decimal`, `Fraction` (and `tuple`, coming in core.05). Lists are mutable.

**Program 1.** `m = n` binds a second name to the int object `5`. `n += 1` cannot alter that
object, so Python computes a new object `6` and rebinds the name `n` to it. `m` still refers to `5`.

**Program 2.** `others = items` binds a second name to the **same** list. `items.append(6)` changes
that list object in place; no rebinding happens. Both names see the change, because there is only
one list. `items is others` stays `True`.

**What `n += 1` does.** For an immutable object, `n += 1` is the same as `n = n + 1`: the old
object is left untouched (and is reclaimed later if nothing else refers to it), and the name `n` now refers to a new object.
For a mutable object like a list, `+=` changes the object in place instead.

**Advantage of immutability.** You can share an immutable object between many names, or pass it
anywhere, without fear that someone else will change it under you. It also allows Python to use
it as a dictionary key and to reuse objects internally.

**Rule of thumb.** Ask "is this rebinding a name, or changing an object?". Assignment and
augmented assignment on immutables rebind. Methods like `append` change objects. If two names
share a mutable object and you want independent data, make an explicit copy (core.05).

Key ideas to check: in-place change vs new object; identity stays for mutation; immutable types listed;
`+=` rebinds for immutables; aliasing; benefit of immutability.
