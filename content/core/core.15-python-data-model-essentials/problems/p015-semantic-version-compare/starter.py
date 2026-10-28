from functools import total_ordering


@total_ordering
class Version:
    def __init__(self, text):
        # TODO: parse "1.10.2" into major, minor, patch ints; ValueError if invalid
        self.text = text

    # TODO: __eq__, __lt__, __hash__, __str__, __repr__
