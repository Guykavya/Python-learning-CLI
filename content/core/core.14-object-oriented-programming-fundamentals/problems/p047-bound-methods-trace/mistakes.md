- Writing `Hi Cy, I am Asha` for `m("Cy")`. A bound method stores the object `a`, not the value of
  `a.name` at the time `m` was made.
- Thinking `a.wave("hello")` passes `a` as the first argument. Functions stored in the instance are
  not bound, so `x` is `"hello"`.
- Writing `wave(Greeter)` for `a.wave(3)`. After `Greeter.wave = wave`, `a` still has its own
  `wave` in its `__dict__`, and that one wins over a normal method on the class.
- Thinking `a.shout("hey")` passes `a`. A `staticmethod` never gets `self`.
- Writing `Greeter` for `c.kind()`. A `classmethod` gets the class of the object it was called on.
- Thinking `f(c, "me")` uses `Greeter.greeting` because `f` came from `Greeter`. Attribute lookup
  always starts at `self`, which is `c`.
- Writing `method` for `Greeter.greet`. Read through the class, a function stays a plain function.
