See the model answer shown when you check. The ideas that must appear:

1. A name is a reference (label) to an object; objects have identity, type and value.
2. Assignment binds a name to an object. It never copies.
3. After `b = a`, both names refer to one object, so `a is b` is `True`.
4. `a + 1` creates a new object because ints are immutable; `a = ...` moves only the label `a`.
5. `id()` of `a` changes, `id()` of `b` does not.
6. The label picture also predicts aliasing with mutable objects such as lists, which the box picture gets wrong.
