def clamp(value, low=0, high=100):
    """Return value limited to the range low..high (swapping low and high if reversed)."""
    if low > high:
        low, high = high, low
    if value < low:
        return low
    if value > high:
        return high
    return value
