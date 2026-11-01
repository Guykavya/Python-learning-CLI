## Approach

The model answer is in `answer.md`. The whole topic rests on one fact: `__getattribute__` *is*
the lookup, and `__getattr__` is what the lookup calls when it fails.

| | `__getattribute__` | `__getattr__` |
|---|---|---|
| Called for | every instance attribute read | only reads that raised `AttributeError` |
| Typical use | logging, access control on all names | proxies, defaults, computed missing names |
| Cost | every read pays | only misses pay |
| Main trap | recursion through `self.x` | recursion when it reads a not-yet-set attribute |
| When it cannot answer | raise `AttributeError` | raise `AttributeError` |

## Check your answer

- Did you say that `__getattr__` runs only after the normal lookup **fails**?
- Did you pick `__getattr__` for both (a) and (b), and explain why `__getattribute__` would be worse?
- Did you write `super().__getattribute__(name)` (or `object.__getattribute__(self, name)`)?
- Did you name `AttributeError` and at least one tool (`hasattr`, `getattr` with a default, `copy`, `pickle`) that depends on it?

## Another way

Prove each claim with a ten-line class that prints inside both hooks (as in problem p005), then
write the answer from what you saw.
