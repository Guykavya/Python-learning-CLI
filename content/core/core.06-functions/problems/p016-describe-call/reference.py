def describe_call(func, *args, **kwargs):
    """Call func(*args, **kwargs) once and return 'name(args) -> repr(result)'."""
    result = func(*args, **kwargs)
    parts = [repr(a) for a in args]
    parts += [f"{k}={v!r}" for k, v in kwargs.items()]
    return f"{func.__name__}({', '.join(parts)}) -> {result!r}"
