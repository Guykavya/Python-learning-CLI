**Names are labels.** In Python every value is an object living in memory, with an identity
(`id`), a type and a value. A name is just a label that refers to an object. Assignment
`name = expression` first evaluates the right side to get an object, then attaches the label to it.

**`b = a` copies nothing.** It evaluates `a`, which gives the object `10`, and attaches a second
label `b` to the **same** object. Now there is one object and two names:

```
a ---> [int 10] <--- b
```

So `a is b` is `True`, and `id(a) == id(b)`.

**`a = a + 1` rebinds `a`.** The right side `a + 1` builds a **new** int object `11` (ints are
immutable; `10` itself never changes). Then the label `a` is moved to `11`. `b` was never
touched, so it still refers to `10`:

```
a ---> [int 11]
b ---> [int 10]
```

Now `a is b` is `False`, and `id(a)` has changed while `id(b)` has not.

**Why "boxes" mislead.** In the box picture, `b = a` would copy the contents into a second box.
That gives the right answer for ints by luck, but it predicts the wrong thing for mutable
objects: with `a = [1]; b = a; a.append(2)`, `b` also shows `[1, 2]`, because there was only one
list all along. The label (sticky note) picture explains both cases.

Key ideas to check: names refer to objects; assignment binds and never copies; `is` / `id` show
identity; ints are immutable so arithmetic makes new objects; rebinding one name does not affect others.
