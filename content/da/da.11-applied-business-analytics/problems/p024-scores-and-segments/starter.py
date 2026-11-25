import pandas as pd


def score_quantile(s, higher_is_better=True, n=5):
    """Scores 1..n of roughly equal size; ties broken by position (rank method 'first'); n is the best score when higher_is_better."""
    raise NotImplementedError


def segment(r, f):
    """One of: Champions, Loyal, New / promising, At risk, Hibernating, Needs attention (rules in the statement)."""
    raise NotImplementedError
