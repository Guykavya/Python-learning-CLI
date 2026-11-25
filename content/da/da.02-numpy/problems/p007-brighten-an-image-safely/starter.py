import numpy as np


def add_clipped(img, delta):
    """img + delta, clipped to 0..255, as a new uint8 array of the same shape."""
    # TODO: this version wraps round. Fix it.
    return img + delta
