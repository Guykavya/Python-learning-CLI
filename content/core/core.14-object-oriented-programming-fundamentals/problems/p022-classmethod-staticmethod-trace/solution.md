## Approach

Write down `cls` for each classmethod call, then do normal attribute lookups on it (chapter
sections 5 and 6).

1. `Shape.describe()`: `cls = Shape` → `Shape has 0 sides`.
2. `Triangle.describe()`: `cls = Triangle`, which defines `sides = 3` → `Triangle has 3 sides`.
3. `t.describe()`: called on an instance, `cls` is `type(t)`, `Triangle` → `Triangle has 3 sides`.
4. `Square.create("s1")`: `cls = Square`. `Square` has no `made` of its own, so `cls.made` is
   `Shape.made`, the one shared list → it becomes `['Square']`. `cls(label)` builds a **Square** →
   `Square s1`.
5. `s.info()`: `self.describe()` gives `Square has 4 sides`; `self.unit()` finds `Square.unit` first →
   `s1: Square has 4 sides in m`.
6. `t.info()`: `Triangle` has no `unit`, so `Shape.unit` → `t1: Triangle has 3 sides in cm`.
7. `Shape.unit(), t.unit(), s.unit()` → `cm cm m`.
8. `t.create("t2")`: `cls = Triangle` → list `['Square', 'Triangle']`, `x` is a Triangle →
   `Triangle ['Square', 'Triangle']`.
9. `Triangle.sides = 30` changes only `Triangle`. `x.describe()` uses `cls = Triangle` → 30 sides;
   `Shape.describe()` still 0 → `Triangle has 30 sides Shape has 0 sides`.

## Output

```text
Shape has 0 sides
Triangle has 3 sides
Triangle has 3 sides
Square s1
s1: Square has 4 sides in m
t1: Triangle has 3 sides in cm
cm cm m
Triangle ['Square', 'Triangle']
Triangle has 30 sides Shape has 0 sides
```

## Complexity

Not applicable.

## Another way

Add `print("cls is", cls.__name__)` at the start of `describe` and `create` and run it. This program
also shows why alternative constructors return `cls(...)`: `Square.create` gives a `Square`, which a
hard-coded `Shape(label)` would not.
