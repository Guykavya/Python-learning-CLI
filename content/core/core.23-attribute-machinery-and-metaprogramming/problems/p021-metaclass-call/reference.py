class SingletonMeta(type):
    """Metaclass: each class using it has exactly one instance (subclasses their own)."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in SingletonMeta._instances:
            # If __init__ raises, the assignment never happens: nothing is remembered.
            SingletonMeta._instances[cls] = super().__call__(*args, **kwargs)
        return SingletonMeta._instances[cls]


class InstanceCounter(type):
    """Metaclass: each class using it counts its successful instance creations."""

    def __init__(cls, name, bases, namespace, **kwargs):
        super().__init__(name, bases, namespace, **kwargs)
        cls.instance_count = 0          # runs once per class, so each class has its own

    def __call__(cls, *args, **kwargs):
        obj = super().__call__(*args, **kwargs)
        cls.instance_count += 1
        return obj
