import functools


def count_calls(cls):
    """Wrap functions, classmethods and staticmethods defined in cls; add cls.call_counts."""
    return cls


def reset_counts(cls):
    """Set every count in cls.call_counts back to 0."""
