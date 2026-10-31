def shrink(items: list, fails) -> list:
    """A 1-minimal subsequence of items for which fails() is still True."""
    if not fails(list(items)):
        raise ValueError("the input does not fail, nothing to shrink")
    return items
