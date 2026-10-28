import inspect
from functools import wraps


def curry(func):
    positional = (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
    needed = sum(
        1
        for p in inspect.signature(func).parameters.values()
        if p.kind in positional and p.default is p.empty
    )

    def make(saved_args, saved_kwargs):
        @wraps(func)
        def curried(*args, **kwargs):
            all_args = saved_args + args
            all_kwargs = {**saved_kwargs, **kwargs}
            if len(all_args) >= needed:
                return func(*all_args, **all_kwargs)
            return make(all_args, all_kwargs)
        return curried

    return make((), {})
