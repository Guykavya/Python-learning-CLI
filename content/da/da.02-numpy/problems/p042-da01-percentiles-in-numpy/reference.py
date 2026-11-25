import numpy as np

NUMPY_METHOD = {
    "inclusive": "linear",
    "exclusive": "weibull",
    "nearest_rank": "inverted_cdf",
}


def percentile(x, p, method="inclusive"):
    """The p-th percentile of x with a da.01 method name, computed by np.percentile."""
    x = np.asarray(x, dtype=float)
    if x.size == 0:
        raise ValueError("no data")
    if not 0 <= p <= 100:
        raise ValueError(f"p={p} must be between 0 and 100")
    if method not in NUMPY_METHOD:
        raise ValueError(f"unknown method {method!r}; use one of {sorted(NUMPY_METHOD)}")
    if method == "exclusive":
        pos = (x.size + 1) * p / 100
        if pos < 1 or pos > x.size:
            raise ValueError(f"position {pos} is outside 1..{x.size} for the exclusive method")
    return float(np.percentile(x, p, method=NUMPY_METHOD[method]))
