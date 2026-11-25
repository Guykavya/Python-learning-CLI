import pandas as pd


def safe_merge(left, right, on, how="left", validate="m:1", measure=None, name="",
               expect_same_rows=True, ledger=None):
    """Your safe_merge from p057 (or chapter 14.1)."""
    raise NotImplementedError


def reconcile(parts, total, label="", tol=0.01):
    """Your reconcile from p058 (or chapter 14.2): returns (ok, difference)."""
    raise NotImplementedError


def analyse(tables):
    """The chapter 15 project: a dict with the answers, the ledger and the checks (see problem.md)."""
    # TODO: 1. build the working table with safe_merge (one ledger)   2. answer each question with groupby / isin
    #       3. reconcile the breakdowns into `checks`   4. return the dict with exactly the keys of problem.md
    raise NotImplementedError
