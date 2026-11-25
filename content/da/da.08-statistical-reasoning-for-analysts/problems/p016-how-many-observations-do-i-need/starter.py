import math
from scipy import stats


def n_for_margin(sd, margin, level=0.95):
    """Smallest whole n with margin of error <= margin for a mean."""
    raise NotImplementedError


def n_for_proportion(margin, p=0.5, level=0.95):
    """Smallest whole n with margin of error <= margin for a proportion."""
    raise NotImplementedError
