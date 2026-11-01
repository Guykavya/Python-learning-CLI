class Locked:
    def __init__(self, **fields):
        for name, value in fields.items():
            setattr(self, name, value)

    # TODO: __setattr__ that refuses once the object is locked
    # TODO: __delattr__ that always refuses
    # TODO: __repr__ like Point(x=1, y=2)
