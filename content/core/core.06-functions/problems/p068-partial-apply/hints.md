## Hint 1

Which values does `g` need to remember? Where do they live after `partial_apply` returns?

## Hint 2

Merging keywords: `{**kwargs, **more_kwargs}` builds a NEW dict where the right side wins (or `kwargs | more_kwargs`, core.05).

## Hint 3

```
def partial_apply(func, *args, **kwargs):
    def g(*more_args, **more_kwargs):
        merged = kwargs | more_kwargs
        return func(*args, *more_args, **merged)
    return g
```
