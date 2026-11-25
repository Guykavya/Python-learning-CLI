import itertools

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss


def worst_slices(frame, y, p, cols, min_rows=120, top=6):
    """Top single-column and pair slices by log-loss gap vs overall."""
    raise NotImplementedError
