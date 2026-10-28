## Hint 1

What does a partly-applied function need to remember? Only two things: the positional arguments
so far (a tuple) and the keywords so far (a dict). If you had a helper `make(saved_args,
saved_kwargs)` that returns a curried function holding those two, what would that function do
when called with more arguments?

## Hint 2

Inside the curried function, build **new** values: `all_args = saved_args + args` and
`all_kwargs = {**saved_kwargs, **kwargs}`. If `len(all_args) >= needed`, call `func`. Otherwise
return `make(all_args, all_kwargs)`. Start with `make((), {})`. Because nothing is changed in
place, every branch stays independent.

## Hint 3

```
curry(func):
    needed = number of params p in signature(func).parameters.values()
             with p.kind in (POSITIONAL_ONLY, POSITIONAL_OR_KEYWORD) and p.default is p.empty
    make(saved_args, saved_kwargs):
        @wraps(func)
        curried(*args, **kwargs):
            all_args = saved_args + args
            all_kwargs = {**saved_kwargs, **kwargs}
            if len(all_args) >= needed: return func(*all_args, **all_kwargs)
            return make(all_args, all_kwargs)
        return curried
    return make((), {})
```
