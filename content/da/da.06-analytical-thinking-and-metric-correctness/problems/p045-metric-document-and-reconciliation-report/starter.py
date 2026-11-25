import pandas as pd


def definition_doc(specs):
    """Markdown with one section per metric (see problem.md)."""
    raise NotImplementedError("a title, a note about IST and half-open months, then one '### name' section per spec")


def reconciliation_report(tables, month):
    """Text with the volume bridge and the cash bridge for one month (see problem.md)."""
    raise NotImplementedError("build both bridges, check that they close, add the jobs behind each line")
