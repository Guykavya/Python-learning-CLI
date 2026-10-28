## Hint 1

For each classmethod call, first write down what `cls` is. Then look up `cls.sides` (does that class
define `sides` itself, or does it get it from `Shape`?). For `cls.made`, does `Square` or `Triangle`
have its own `made`, or is there only one list?

## Hint 2

```
Shape.describe()      cls = Shape      sides 0
Triangle.describe()   cls = Triangle   sides 3
t.describe()          cls = Triangle   (type of t)
Square.create("s1")   cls = Square     made is Shape's one list -> append "Square"; returns Square("s1")
s.info()              self.describe() -> cls = Square; self.unit() -> Square.unit -> "m"
t.info()              Triangle has no unit of its own -> Shape.unit -> "cm"
t.create("t2")        cls = Triangle -> append "Triangle"; returns a Triangle
Triangle.sides = 30   only Triangle changes
```
