def bind(func, obj):
    """Return func bound to obj, exactly as obj.func would be if func lived on the class."""
    return func.__get__(obj, type(obj))


def method_parts(method):
    """Split a bound method into (function, instance)."""
    return method.__func__, method.__self__


def rebind(method, other):
    """Bind the same underlying function to another object."""
    return method.__func__.__get__(other, type(other))
