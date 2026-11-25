import numpy as np


def to_gray(img):
    """(H, W, 3) uint8 -> (H, W) uint8 with weights 0.299, 0.587, 0.114."""
    # TODO
    raise NotImplementedError


def adjust(img, brightness=0, contrast=1.0):
    """(img - 128) * contrast + 128 + brightness, rounded, clipped, uint8."""
    # TODO
    raise NotImplementedError


def flip(img, how):
    """'horizontal' (left-right) or 'vertical' (top-bottom); a copy."""
    # TODO
    raise NotImplementedError


def blur3(img):
    """3 x 3 box blur of a grey image with edge padding, rounded, uint8."""
    # TODO
    raise NotImplementedError


def equalise(img):
    """Histogram equalisation with a 256-entry lookup table."""
    # TODO
    raise NotImplementedError


def pipeline(img, steps):
    """Apply each step in order; no steps -> a copy."""
    # TODO
    raise NotImplementedError
