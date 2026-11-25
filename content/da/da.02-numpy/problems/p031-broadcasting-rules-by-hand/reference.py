def broadcast_shape(*shapes):
    """The broadcast result shape as a tuple; ValueError naming the axis if incompatible."""
    if not shapes:
        return ()
    ndim = max(len(s) for s in shapes)
    padded = [(1,) * (ndim - len(s)) + tuple(int(n) for n in s) for s in shapes]
    result = [1] * ndim
    for axis in range(ndim - 1, -1, -1):
        lengths = [s[axis] for s in padded]
        not_one = sorted({n for n in lengths if n != 1})
        if len(not_one) > 1:
            raise ValueError(f"cannot broadcast: axis {axis} has lengths {not_one[0]} and {not_one[1]}")
        result[axis] = not_one[0] if not_one else 1
    return tuple(result)
