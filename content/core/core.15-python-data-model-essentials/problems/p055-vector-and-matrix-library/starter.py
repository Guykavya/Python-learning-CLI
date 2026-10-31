class Vector:
    def __init__(self, *components):
        # TODO: validate (at least one number) and store as a tuple
        self._c = tuple(components)


class Matrix:
    def __init__(self, rows):
        # TODO: validate (rectangular, non-empty, numbers) and store as a tuple of tuples
        self._rows = tuple(tuple(r) for r in rows)
