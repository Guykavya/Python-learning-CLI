import numpy as np


def rule_score(X):
    return (2 * X["contract_month"].to_numpy() + 1 * (X["support_calls"].to_numpy() >= 3)).astype(float)
