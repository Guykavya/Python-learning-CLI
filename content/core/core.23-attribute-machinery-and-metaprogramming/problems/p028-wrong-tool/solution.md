## Approach

The model answer is in `answer.md`. The rule behind it: use the tool that runs at exactly the
moment you need, and no earlier and no more often.

| Need | Lightest tool |
|---|---|
| standard methods generated from fields | `@dataclass` |
| a computed value when one attribute is read | `property` |
| run code once per subclass (register, check) | `__init_subclass__` or a class decorator |
| behaviour that needs no class at all | a plain function |
| operations on the class object itself, or a custom class namespace | metaclass |

## Check your answer

- Did you pick `@dataclass` for A, `property` for B and `__init_subclass__` (or a decorator) for C, and show the key lines?
- For each, did you give two *concrete* costs (what breaks, who cannot see what), not just "too complex"?
- Did you mention that tools (IDE, type checker, `dir()`) cannot see attributes created by magic?
- Did you find the bug in B: `return None` for unknown names hides typos and makes `hasattr` always `True`?
- Did you notice in A that `zip` silently drops extra arguments, or that `__eq__` without `__hash__` makes instances unhashable?
- Did you mention metaclass conflicts for C?
- Did your justified case need something only a metaclass has (`__prepare__`, or methods like `__len__`/`__iter__`/`__call__` that act on the class)?

## Another way

You can also answer part 3 with an ORM: a model class where `User.name == "Ann"` builds a query
object needs operators on the *descriptor*, not a metaclass; but a model registry with
`len(User)` returning the number of rows or `for row in User` would need methods on the class's
type, which is a metaclass. Saying *why* a lighter tool cannot do it is what counts.
