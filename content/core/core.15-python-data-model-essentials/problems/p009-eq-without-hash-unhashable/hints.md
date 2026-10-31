## Hint 1

For every class ask: did it define `__eq__`? did it define `__hash__` in its own body? If it defined `__eq__` only, Python sets `__hash__ = None` for that class.

## Hint 2

```
P: __eq__ only          -> P.__hash__ is None -> hash(P(1)) raises TypeError
Q: __eq__ and __hash__  -> hashable
S(Q): new __eq__ only   -> S.__hash__ is None again
```
