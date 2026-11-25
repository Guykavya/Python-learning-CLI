from pathlib import Path

import matplotlib.pyplot as plt


def make_figures(sales_df):
    """Four (name, fig, alt) tuples: trend, stores, categories, weekdays. Titles computed from the data; every figure passes the linter."""
    raise NotImplementedError


def build_report(sales_df, folder):
    """Save <name>.png for each figure (dpi 100) and report.md in folder; return the five Paths; leave no figure open."""
    raise NotImplementedError
