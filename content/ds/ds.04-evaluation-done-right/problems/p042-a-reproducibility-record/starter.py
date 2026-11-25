import dataclasses
import hashlib

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


def data_fingerprint(df):
    """First 16 hex chars of SHA-256 over the column names and the row hashes."""
    raise NotImplementedError


def run_experiment(cfg, df):
    """Record with config, data fingerprint and rows, and test metrics."""
    raise NotImplementedError
