import numpy as np

WEIGHTS = np.array([0.299, 0.587, 0.114])


def to_gray(img):
    """(H, W, 3) uint8 -> (H, W) uint8 with weights 0.299, 0.587, 0.114."""
    img = np.asarray(img)
    if img.ndim != 3 or img.shape[2] != 3:
        raise ValueError(f"expected a colour image of shape (H, W, 3), got {img.shape}")
    return np.round(img.astype(float) @ WEIGHTS).astype(np.uint8)


def adjust(img, brightness=0, contrast=1.0):
    """(img - 128) * contrast + 128 + brightness, rounded, clipped, uint8."""
    out = (np.asarray(img).astype(float) - 128.0) * contrast + 128.0 + brightness
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


def flip(img, how):
    """'horizontal' (left-right) or 'vertical' (top-bottom); a copy."""
    img = np.asarray(img)
    if how == "horizontal":
        return img[:, ::-1].copy()
    if how == "vertical":
        return img[::-1].copy()
    raise ValueError(f"how must be 'horizontal' or 'vertical', got {how!r}")


def blur3(img):
    """3 x 3 box blur of a grey image with edge padding, rounded, uint8."""
    img = np.asarray(img)
    if img.ndim != 2:
        raise ValueError(f"blur3 expects a grey (H, W) image, got shape {img.shape}")
    h, w = img.shape
    padded = np.pad(img.astype(float), 1, mode="edge")
    total = np.zeros((h, w))
    for dy in range(3):
        for dx in range(3):
            total += padded[dy:dy + h, dx:dx + w]
    return np.round(total / 9).astype(np.uint8)


def equalise(img):
    """Histogram equalisation with a 256-entry lookup table."""
    img = np.asarray(img)
    counts = np.bincount(img.ravel(), minlength=256)
    cdf = counts.cumsum()
    first = cdf[counts > 0][0]
    if cdf[-1] == first:
        return img.copy()
    lut = np.clip(np.round((cdf - first) / (cdf[-1] - first) * 255), 0, 255).astype(np.uint8)
    return lut[img]


def pipeline(img, steps):
    """Apply each step in order; no steps -> a copy."""
    out = np.asarray(img).copy()
    for step in steps:
        out = step(out)
    return out
