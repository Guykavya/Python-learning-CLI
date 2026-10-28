## Approach

Follow the chain for each `==`: left operand first; `NotImplemented` means "ask the other side"; a real `True` or `False` ends the search.

## Output

```text
Strict.eq
True
Strict.eq
Always.eq
True
Always.eq
True
Loose.eq
False
Strict.eq
False
Strict.eq
Always.eq
False
Loose.eq
True
```

## Complexity

Not applicable.

## Another way

Add a `__ne__` that prints too and see which one Python calls for `!=`.
