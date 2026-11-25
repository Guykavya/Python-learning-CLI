import json

import pandas as pd


def model_from_project(folder, Model):
    """Build (model, spec) from folder/model_spec.json and the data files; ValueError('relationship <from> -> <to>: ...') for a refused relationship."""
    raise NotImplementedError


def check_report_spec(report, model, spec):
    """List of problems: unknown slicer fields, measures and axis/rows/columns fields of a report specification."""
    raise NotImplementedError
