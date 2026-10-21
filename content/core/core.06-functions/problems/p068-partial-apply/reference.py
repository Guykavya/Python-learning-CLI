def partial_apply(func, *args, **kwargs):
    """Return g where g(*more, **more_kw) == func(*args, *more, **(kwargs | more_kw))."""
    def g(*more_args, **more_kwargs):
        merged = kwargs | more_kwargs
        return func(*args, *more_args, **merged)
    return g
