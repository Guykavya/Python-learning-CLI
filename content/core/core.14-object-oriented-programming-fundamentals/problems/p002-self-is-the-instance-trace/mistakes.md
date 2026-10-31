- Forgetting that `a.tick()` and `a.tick(5)` return values that are thrown away. Only the
  `print(b.tick())` line prints a number.
- Thinking `c = a` makes a copy. It is a second name for the same object, so `c.tick(100)` changes `a`.
- Thinking `Counter.tick(b, 2)` changes the class or every counter. It is the same as `b.tick(2)`.
- Writing `0 0 0` after `b.reset()`. `reset` only changes `self`, which is `b` here.
- Thinking `r = a.tick` calls the method, or that `r()` fails without an object. A bound method
  remembers its object.
