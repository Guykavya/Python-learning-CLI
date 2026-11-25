import numpy as np
import pandas as pd


def retention_matrix(orders, customers, asof):
    """Rows: cohort Period; columns: months since the cohort month; shares of the cohort; NaN where not yet observable."""
    raise NotImplementedError
