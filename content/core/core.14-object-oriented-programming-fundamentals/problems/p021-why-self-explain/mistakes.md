- Saying `self` is a keyword. It is a normal parameter name; only the position (first) matters.
- Saying `self` is the class. In a normal method it is the instance; the class is `type(self)`.
- Missing the second bug. `count = 0` without `self.` stores nothing on the object.
- Explaining "1 was given" as a Python bug. The hidden argument is the object itself.
- Giving only "explicit is better than implicit" as a reason. Explain what it buys you: attribute vs
  local is visible, and methods stay plain functions.
