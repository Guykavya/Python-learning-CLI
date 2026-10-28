## Hint 1

Where does validation code go when you do not write `__init__` yourself? What name does the generated `__init__` call at the end? And which field options keep `history` and `area` out of the constructor's parameters?

## Hint 2

For `Rectangle`, the generated `__init__` has the parameters `width`, `height`, `unit_scale`; the last one is an `InitVar`, so it is passed on as `__post_init__(self, unit_scale)`. Fields with defaults must come after fields without: `area` has `init=False` and needs no default, but `unit_scale` has a default, so is `area` allowed after it? (Yes: `init=False` fields are not parameters, so the rule does not apply to them.)

## Hint 3

```
Account.__post_init__: validate owner (str and non-blank) and balance (>= 0)
                       self.owner = owner.strip().title() ; history.append(("open", balance))
Range.__post_init__: raise ValueError for step <= 0 or low > high   (no assignments: frozen)
Rectangle.__post_init__(unit_scale): width *= unit_scale ; height *= unit_scale ; area = width * height
```
