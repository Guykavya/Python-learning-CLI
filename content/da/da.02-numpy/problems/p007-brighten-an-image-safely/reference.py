import numpy as np


def add_clipped(img, delta):
    wide = img.astype(np.int16) + delta
    return np.clip(wide, 0, 255).astype(np.uint8)
