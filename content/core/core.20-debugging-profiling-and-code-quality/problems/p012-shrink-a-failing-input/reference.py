def shrink(items: list, fails) -> list:
    """A 1-minimal subsequence of items for which fails() is still True."""
    current = list(items)
    if not fails(list(current)):
        raise ValueError("the input does not fail, nothing to shrink")
    chunk = max(len(current) // 2, 1)
    while current:
        removed = False
        i = 0
        while i < len(current):
            candidate = current[:i] + current[i + chunk:]
            if fails(list(candidate)):
                current = candidate  # keep the smaller input, try the same position again
                removed = True
            else:
                i += chunk
        if not removed:
            if chunk == 1:
                break  # a full pass removed nothing: 1-minimal
            chunk = max(chunk // 2, 1)
    return current
