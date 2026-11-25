import numpy as np
import pandas as pd


def age_bands(s):
    """Label ages: youth (<= 18), adult (<= 40), middle (<= 65), senior (above); edges are right-closed."""
    # TODO: pd.cut with edges, labels and include_lowest
    raise NotImplementedError


def spend_quartiles(s):
    """Label values Q1 (lowest quarter) to Q4 with pd.qcut."""
    # TODO: pd.qcut with q=4 and the four labels
    raise NotImplementedError
