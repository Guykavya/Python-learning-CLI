## Approach

Treat the program as three events and walk through the class creation protocol for each.

## Trace

**Event 1: `class Base(metaclass=Meta)`.**

- `Meta.__prepare__("Base", ())` prints `1 prepare Base {}` (no keywords).
- The body defines only `__init_subclass__`, which starts with `__`, so `own` is empty:
  `2 meta new Base []`.
- Inside `type.__new__`: no attribute has `__set_name__`, and the parent of `Base` is `object`,
  whose `__init_subclass__` prints nothing. `Base.__init_subclass__` is **not** called for `Base`
  itself; it is a hook for future subclasses.
- `3 meta new done Base`, then `4 meta init Base`.

**Event 2: the decorated `class Point(Base, tag="p")`.**

- `--- define Point` is a normal print. The expression `deco` is evaluated (nothing printed).
- `1 prepare Point {'tag': 'p'}`: the class keyword arrives at `__prepare__`.
- The body runs top to bottom in the namespace: `body start`, `field first`, `field second`,
  `body end`. The methods are just stored; nothing prints for them.
- `2 meta new Point ['x', 'y', 'norm']`: the namespace keeps definition order; `__new__`,
  `__init__` and the hidden entries such as `__module__` and `__qualname__` start with `__`.
- `super().__new__` is `type.__new__`. It creates the class, then calls `__set_name__` on every
  attribute that has one: `set_name Point.x (first)`, `set_name Point.y (second)`. Then it calls
  the parent's hook with the keywords: `init_subclass Point {'tag': 'p'}`.
- Back in `Meta.__new__`: `3 meta new done Point`. Then `4 meta init Point`.
- Only now is the decorator called: `decorate Point`.

**Event 3: `Point(1, 2)`.**

- `Point(1, 2)` is `type(Point).__call__(Point, 1, 2)` = `Meta.__call__`: `5 meta call Point (1, 2)`.
- `super().__call__` is `type.__call__`, which calls `Point.__new__` (`Point new`) and then,
  because the result is an instance of `Point`, `Point.__init__` (`Point init 1 2`).
- `6 meta call done Point`, and the last line `--- done Meta Point`.

| Step | Lines |
|---|---|
| `Base` created | `1 prepare Base {}` ... `4 meta init Base` |
| `Point` body | `body start`, `field first`, `field second`, `body end` |
| `type.__new__` inside `Meta.__new__` | `set_name ...` twice, then `init_subclass Point {'tag': 'p'}` |
| after the class exists | `3 ...`, `4 ...`, then `decorate Point` |
| instance | `5 ...`, `Point new`, `Point init 1 2`, `6 ...` |

## Another way

Put `import traceback; traceback.print_stack(limit=4)` inside `__set_name__` and inside
`__init_subclass__`. The stack shows `Meta.__new__` above both, which proves they run
*inside* `type.__new__`, not after it. Remove the decorator and the `__call__` method to see
which lines disappear.
