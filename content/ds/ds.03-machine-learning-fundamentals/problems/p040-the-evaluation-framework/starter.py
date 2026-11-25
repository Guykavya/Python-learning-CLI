import math

import numpy as np
import pandas as pd
from sklearn import dummy, metrics, model_selection


class TestSetAlreadyOpened(RuntimeError):
    """Raised when the sealed test set is requested a second time."""


class Evaluation:
    def __init__(self, X, y, task="regression", test_size=0.2, seed=0):
        raise NotImplementedError

    def compare(self, models):
        raise NotImplementedError

    def baseline(self):
        raise NotImplementedError

    def learning_curve(self, model, sizes=(0.1, 0.25, 0.5, 0.75, 1.0)):
        raise NotImplementedError

    @staticmethod
    def diagnose(lc, task="regression"):
        raise NotImplementedError

    def tune(self, model, grid):
        raise NotImplementedError

    def final_test(self, model):
        raise NotImplementedError
