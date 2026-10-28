**1. What `self` is.** `self` is an ordinary parameter: the first parameter of every normal method.
It holds the object the method was called on. In `c.tick()`, `self` is `c`. In `d.tick()` it would be
`d`. That is how one function, written once in the class, can work on many different objects.

**2. What the call becomes.** `c.tick()` is short for `Counter.tick(c)`. Python looks up `tick` on the
class, makes a *bound method* that remembers `c`, and passes `c` as the first argument. So Ravi did
pass one argument, the object itself, invisibly. His `def tick():` accepts zero, hence "takes 0
positional arguments but 1 was given". The fix is `def tick(self):`.

**3. The second bug.** `count = 0` inside `__init__` creates a **local variable** that disappears
when `__init__` returns. The object gets no attribute. After fixing `tick`, `self.count += 1` would
fail with `AttributeError: 'Counter' object has no attribute 'count'`, because `self.count += 1` first
**reads** `self.count`. The fix is `self.count = 0`.

**4. Why explicit.**
- *Reading code:* `self.count` is obviously an attribute of the object; `count` is obviously a local
  variable. In Java, `count` might be either, and you have to look elsewhere to know.
- *No hidden rule for assignment:* Python creates a local variable whenever you assign to a plain
  name. Without `self.`, it could not tell "set a local" from "set an attribute".
- *Methods are plain functions:* a method is just a function stored in a class. `Counter.tick(c)`
  works, and so does calling a parent's version, `Parent.method(self)` (or `super().method()`).
  No special "method" machinery is needed.
- "Explicit is better than implicit" (the Zen of Python).

**5. The name.** `self` is only a strong convention. Any name works, `def tick(this):`, but every
Python programmer and tool expects `self`, so always use it. (Class methods use `cls` by the same
convention.)
