class Record:
    """Base class for table records. Subclasses must define `table` and `fields`.

    Write __init_subclass__, __init__ and __repr__.
    """

    def __init_subclass__(cls, abstract=False):
        pass

    def __init__(self, **values):
        for name, value in values.items():
            setattr(self, name, value)
