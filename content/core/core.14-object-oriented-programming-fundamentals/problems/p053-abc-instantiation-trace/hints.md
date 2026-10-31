## Hint 1

For each class, list the abstract names it inherits and cross out the ones it (or a parent between it
and `Shape`) overrides. `Square` overrides `area`; what is still left? `NamedSquare` inherits `area`
from `Square` and adds `name`. Does it matter that the two methods come from different classes?

## Hint 2

`Triangle.area` calls `super().area()`, which runs the body of the abstract `Shape.area`. What does that
body return? For `register`: it makes `isinstance` and `issubclass` say `True`, but does it put `Shape`
into `Blob.__mro__`? Where would `blob.describe` have to come from?

```text
Shape        abstract left: area, name   -> cannot
Square       abstract left: name         -> cannot
NamedSquare  abstract left: (none)       -> ok
Triangle     abstract left: (none)       -> ok
Blob         not a real subclass, no ABC rules at all -> ok
```
