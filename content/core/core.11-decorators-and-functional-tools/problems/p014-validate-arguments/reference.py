from functools import wraps


def typed(*types):
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            name = func.__name__
            if len(args) != len(types):
                raise TypeError(f"{name}() expects {len(types)} positional arguments, got {len(args)}")
            for i, (arg, wanted) in enumerate(zip(args, types), start=1):
                if not isinstance(arg, wanted):
                    raise TypeError(
                        f"{name}() argument {i} must be {wanted.__name__}, got {type(arg).__name__}"
                    )
            return func(*args, **kwargs)
        return wrapper
    return decorate


def in_range(low, high):
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for i, arg in enumerate(args, start=1):
                if isinstance(arg, (int, float)) and not (low <= arg <= high):
                    raise ValueError(f"{func.__name__}() argument {i} = {arg} is outside {low}..{high}")
            return func(*args, **kwargs)
        return wrapper
    return decorate
